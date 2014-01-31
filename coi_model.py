# -*- coding: utf-8; mode: django -*-

'''
One of the more complex Django models I have built for a large application at Rice.
'''


import reversion
from reversion.revisions import revision_context_manager
from datetime import datetime

from django.db import models
from django_fsm.db.fields import FSMField, transition

from ws.emailtemplates.models import Template as EmailTemplate

from riceuser.models import UserProfile, Department
from annual.functions import lazyproperty, get_object_or_none, add_to_revision


class ReportingSeason(models.Model):
    year = models.SmallIntegerField(unique=True)
    conflict_cutoff = models.DateField()
    date_open = models.DateTimeField()
    deadline = models.DateTimeField()

    def __unicode__(self):
        return u"%s" % self.year

    def is_open(self, today=None):
        """
        Annual Report could be submitted
        """
        if not today:
            today = datetime.today()
        return self.date_open <= today and self.deadline >= today

    @staticmethod
    def current(today=None):
        if today == None:
            today = datetime.today()

        try:
            season = ReportingSeason.objects.get(year=today.year)
        except ReportingSeason.DoesNotExist:
            return None
        else:
            return season

#
# Reports
#

class AnnualReport(models.Model):
    class STATUS:
        UNSUBMITTED = 'U'
        REVISING = 'R'
        PENDING = 'P'
        NO_CONFLICTS = 'N'
        COMMITTEE_REVIEW = 'E'
        PLAN_SUBMITTED = 'M'
        CANT_MANAGED = 'C'

    STATUS_CHOICES = ((STATUS.UNSUBMITTED,'Unsubmitted'),
                      (STATUS.REVISING,'Revising'),
                      (STATUS.PENDING,'Pending Review'),
                      (STATUS.NO_CONFLICTS,'Finalized (No Conflicts)'),
                      (STATUS.COMMITTEE_REVIEW, 'Pending Committee Review'),
                      (STATUS.PLAN_SUBMITTED,'Finalized (Management Plan Submitted)'),
                      (STATUS.CANT_MANAGED, 'Finalized (Conflicts Cannot Be Managed)'),)

    user = models.ForeignKey(UserProfile)
    year = models.SmallIntegerField()
    department = models.ForeignKey(Department)

    have_gift = models.BooleanField()
    have_conflict_income = models.BooleanField()
    have_conflict_activities = models.BooleanField()
    have_travel_activities = models.BooleanField()
    
    committee_member_1 = models.ForeignKey(UserProfile, related_name='committee_member_1', blank=True, null=True, default=None)
    committee_member_2 = models.ForeignKey(UserProfile, related_name='committee_member_2', blank=True, null=True, default=None)

    status = FSMField(max_length=1, choices=STATUS_CHOICES, default=STATUS.UNSUBMITTED)
    created = models.DateTimeField(auto_now_add=True)
    dean_manageable = models.BooleanField(default=False)

    @property
    def have_conflicts(self):
        return self.have_conflict_income \
            or self.have_conflict_activities \
            or self.have_travel_activities \
            or self.have_gift

    @lazyproperty
    def submission(self):
        return ReportSubmission.objects.exclude(status=ReportSubmission.STATUS.REJECTED).get(report=self)
    
    @lazyproperty
    def season(self):
        return get_object_or_none(ReportingSeason, year=self.year)

    @property
    def is_editable(self):
        return self.status in [ AnnualReport.STATUS.UNSUBMITTED,
                                    AnnualReport.STATUS.REVISING ]
    
    def __unicode__(self):
        return u"%s, %s %s (%s)" % (self.user.user.last_name,self.user.user.first_name,self.year,self.get_status_display())

    def is_interim_open(self, today=None):
        """
        Interim Report could be submitted
        """
        if not today:
            today = datetime.today()
        return today.year == self.year


    def submissions_reminders(self):
        try:
            submission = ReportSubmission.objects.filter(report=self).latest()
            return Reminder.objects.filter(report=self, sent__gt=submission.date_submitted)
        except ReportSubmission.DoesNotExist:
            return Reminder.objects.filter(report=self)

    def can_be_submitted(self):
        income_done = not self.have_conflict_income \
                      or bool(self.incomeconflict_set.all())

        activities_done = not self.have_conflict_activities \
                          or bool(self.consultingconflict_set.all())

        travel_done = not self.have_travel_activities \
                      or bool(self.travelconflict_set.all())

        return self.status in AnnualReport.STATUS.UNSUBMITTED \
               and income_done and activities_done and travel_done

    def need_revising(self):
        return self.status == AnnualReport.STATUS.REVISING

    def can_sent_to_revise(self):
        return self.submission.status in [ ReportSubmission.STATUS.DEAN_REVIEW,
                                           ReportSubmission.STATUS.OSR_REVIEW ]

    def can_be_revised(self):
        return self.submission.status in [ ReportSubmission.STATUS.PENDING,
                                           ReportSubmission.STATUS.PENDING_OSR ]
    def can_has_conflict(self):
        return self.submission.status in [ ReportSubmission.STATUS.DEAN_REVIEW,
                                           ReportSubmission.STATUS.OSR_REVIEW_NO_CONFLICTS,
                                           ReportSubmission.STATUS.OSR_REVIEW,
                                           ReportSubmission.STATUS.OSR_REVIEW_USER_DOC,
                                           ReportSubmission.STATUS.USER_INFO]

    @transition(field=status, source=STATUS.UNSUBMITTED, target=STATUS.PENDING, conditions=[can_be_submitted])
    def submit(self):
        """
        Send report to Dean
        """
        reviewer = ReportSubmission.STATUS.DEAN_REVIEW

        ReportSubmission.objects.create(report=self, status=reviewer)

    @transition(field=status, source=STATUS.PENDING, target=STATUS.UNSUBMITTED)
    def reject(self):
        """
        Report rejected
        """
        self.submission._reject()
        self.submission.save()
        del self.submission

    def acknowledge(self):
        self.submission._acknowledge()
        self.submission.save()

    @transition(field=status, source=STATUS.PENDING)
    def approve(self):
        self.submission._dean_approve()
        self.submission.save()

    @transition(field=status, source=STATUS.PENDING, conditions = [ can_has_conflict ])
    def has_conflict(self):
        if self.submission.status == ReportSubmission.STATUS.DEAN_REVIEW:
            self.submission._dean_conflict_found()
        elif self.submission.status == ReportSubmission.STATUS.OSR_REVIEW_NO_CONFLICTS:
            self.submission._osr_conflict_found()
        elif self.submission.status == ReportSubmission.STATUS.OSR_REVIEW:
            self.submission._info_requested()
        elif self.submission.status == ReportSubmission.STATUS.USER_INFO:
            self.submission._info_submitted()
        elif self.submission.status == ReportSubmission.STATUS.OSR_REVIEW_USER_DOC:
            self.submission._info_unacceptable()
        else:
            raise NotImplementedError('Unknown submission state for has_conflict')
        self.submission.save()
    
    @transition(field=status, source=STATUS.PENDING, target=STATUS.COMMITTEE_REVIEW)
    def members_selected(self):
        if self.submission.status == ReportSubmission.STATUS.OSR_REVIEW_USER_DOC:
            self.submission._pending_committee()
        else:
            raise NotImplementedError('Unknown submission state for members_selected')
        self.submission.save()
            
    @transition(field=status, source=STATUS.PENDING, target=STATUS.REVISING, conditions=[ can_sent_to_revise ])
    def revise(self):
        """
        Return report for faculty member revising
        """
        if self.submission.status == ReportSubmission.STATUS.DEAN_REVIEW:
            self.submission._revise()
        elif self.submission.status == ReportSubmission.STATUS.OSR_REVIEW:
            self.submission._revise_osr()
        else:
            raise NotImplementedError('Unknown submission status for revise')
        self.submission.save()

    @transition(field=status, source=STATUS.REVISING, target=STATUS.PENDING, conditions=[ can_be_revised ])
    def revised(self):
        """
        Done information editing
        """
        if self.submission.status == ReportSubmission.STATUS.PENDING:
            self.submission._revised()
        elif self.submission.status == ReportSubmission.STATUS.PENDING_OSR:
            self.submission._revised_osr()
        else:
            raise NotImplementedError('Unknown submission status for revise')
        self.submission.save()
        
    @transition(field=status, source=STATUS.COMMITTEE_REVIEW, target=STATUS.PENDING)
    def committee_done(self):
        """
        Send committee done, waiting for OSR final recommendations
        """
        if self.submission.status == ReportSubmission.STATUS.COMMITTEE_REVIEW:
            self.submission._committee_done()
        else:
            raise NotImplementedError('Unknown submission status for management change') 
              
        self.submission.save()
        
    def management_plan_required(self):
        if self.submission.status == ReportSubmission.STATUS.OSR_FINAL_REVIEW:
            self.submission._management_plan_required()
        else:
            raise NotImplementedError('Unknown submission status for management change') 
              
        self.submission.save()

    @transition(field=status, source=STATUS.PENDING, target=STATUS.NO_CONFLICTS)
    def done_no_conflicts(self):
        """
        Ok, no conflicts found
        """
        self.submission._accept()
        self.submission.save()

    @transition(field=status, source=STATUS.COMMITTEE_REVIEW, target=STATUS.PLAN_SUBMITTED)
    def done_with_management_plan(self):
        """
        Ok, manangement plan added
        """
        self.submission._management_plan_done()
        self.submission.save()

    @transition(field=status, source=STATUS.COMMITTEE_REVIEW, target=STATUS.CANT_MANAGED)
    def done_cant_be_managed(self):
        """
        Conflicts can not be managed
        """
        self.submission._cant_manage()
        self.submission.save()

    def save_with_revision(self, author=None):        
        revision_context_manager.start()
        if author:
            revision_context_manager.set_user(author)

        self.save()
        try:
            add_to_revision(self)

            try:
                add_to_revision(self.submission)
            except ReportSubmission.DoesNotExist:
                """
                Saving for Interim Report
                """

            if self.have_conflict_income:
                for income in self.incomeconflict_set.all():
                    add_to_revision(income)
            if self.have_conflict_activities:
                for business in self.businessconflict_set.all():
                    add_to_revision(business)
                for consulting in self.consultingconflict_set.all():
                    add_to_revision(consulting)
                for travel in self.travelconflict_set.all():
                    add_to_revision(travel)
        except:
            revision_context_manager.invalidate()
            raise
        finally:
            revision_context_manager.end()

    class Meta:
        unique_together = ('user', 'year')
        permissions = [ ('can_view_all_reports', 'Can view all reports'),
                        ('can_search_reports', 'Can search reports'),
                        ('can_make_osr_review', 'Can make OSR review'),
                        ('can_make_committee_recommendation', 'Can make committee recommendation') ]



class ReportSubmission(models.Model):
    class STATUS:
        REJECTED = 'X'
        DEAN_REVIEW = 'D'
        OSR_REVIEW = 'O'
        OSR_REVIEW_NO_CONFLICTS = 'N'
        OSR_FINAL_REVIEW = 'F'
        OSR_REVIEW_USER_DOC = 'W'
        PENDING = 'P'
        PENDING_OSR = 'E'
        USER_INFO = 'U'
        PENDING_COMMITTEE = 'Z'
        COMMITTEE_REVIEW = 'R'
        COMMITTEE_MANAGEMENT = 'M'
        ACCEPTED = 'A'
        CANT_MANAGE = 'B'

    STATUS_CHOICES = (
        (STATUS.REJECTED, 'Rejected'),
        (STATUS.DEAN_REVIEW, 'Dean Review Pending'),
        (STATUS.OSR_REVIEW, 'ORC Review Pending, COI Identified'),
        (STATUS.OSR_REVIEW_NO_CONFLICTS, 'ORC Review Pending, no COI'),
        (STATUS.PENDING, 'Pending Additional Information'),
        (STATUS.PENDING_OSR, 'Pending Additional Information for ORC'),
        (STATUS.OSR_REVIEW_USER_DOC, 'ORC Reviewing user documentation'),
        (STATUS.USER_INFO, 'OSR Requesting Further Information'),
        (STATUS.PENDING_COMMITTEE, 'Pending Committee Assignment'),
        (STATUS.COMMITTEE_REVIEW, 'Committee Review'),
        (STATUS.COMMITTEE_MANAGEMENT, 'Committee Management'),
        (STATUS.OSR_FINAL_REVIEW, 'ORC Final Recommendation Review'),
        (STATUS.ACCEPTED, 'Dean and ORC Review Complete'),
        (STATUS.CANT_MANAGE, 'Not able to be managed'),
    )

    report = models.ForeignKey(AnnualReport)
    date_submitted = models.DateTimeField(auto_now_add=True)
    status = FSMField(max_length=1, choices=STATUS_CHOICES, protected=True)
    date_resolved = models.DateTimeField(null=True)

    additional_comment = models.TextField(default="")
    osr_requested_info = models.TextField(default="")

    @property
    def timestamp(self):
        return self.date_submitted.strftime('%Y%m%d%H%M')

    @property
    def osr_can_identify_conflict(self):
        return self.status == ReportSubmission.STATUS.OSR_REVIEW

    @transition(field=status, source=[STATUS.DEAN_REVIEW, STATUS.COMMITTEE_REVIEW], target=STATUS.REJECTED)
    def _reject(self):
        """
        Completly incorrect review
        """
        self.date_resolved = datetime.now()


    @transition(field=status, source=STATUS.DEAN_REVIEW, target=STATUS.PENDING)
    def _revise(self):
        """
        Additional info required
        """

    @transition(field=status, source=STATUS.OSR_REVIEW, target=STATUS.PENDING_OSR)
    def _revise_osr(self):
        """
        Additional info required for OSR
        """

    @transition(field=status, source=STATUS.PENDING, target=STATUS.DEAN_REVIEW)
    def _revised(self):
        """
        Report refined, back to dean review

        DO NOT USE this method directly. Use AnnualReport.revised() instead
        """

    @transition(field=status, source=STATUS.PENDING_OSR, target=STATUS.OSR_REVIEW)
    def _revised_osr(self):
        """
        Report refined, back to osr review

        DO NOT USE this method directly. Use AnnualReport.revised() instead
        """

    @transition(field=status, source=STATUS.DEAN_REVIEW, target=STATUS.OSR_REVIEW_NO_CONFLICTS)
    def _dean_approve(self):
        """
        Report approved by dean, no conflicts found
        """

    @transition(field=status, source=STATUS.DEAN_REVIEW, target=STATUS.OSR_REVIEW)
    def _dean_conflict_found(self):
        """
        Dean found conflict, send to OSR for conflict review
        """

    @transition(field=status, source=STATUS.OSR_REVIEW_NO_CONFLICTS, target=STATUS.DEAN_REVIEW)
    def _osr_conflict_found(self):
        """
        OSR found conflict not identified by dean, sending back
        """
        
    @transition(field=status, source=STATUS.OSR_REVIEW, target=STATUS.USER_INFO)
    def _info_requested(self):
        """
        OSR found conflicts, need to get info from user
        """
    
    @transition(field=status, source=STATUS.USER_INFO, target=STATUS.OSR_REVIEW_USER_DOC)
    def _info_submitted(self):
        """
        User submits information - return to OSR for review
        """
    
    @transition(field=status, source=STATUS.OSR_REVIEW_USER_DOC, target=STATUS.USER_INFO)
    def _info_unacceptable(self):
        """
        Information not acceptable, return to user
        """
        
    @transition(field=status, source=STATUS.OSR_REVIEW_USER_DOC, target=STATUS.PENDING_COMMITTEE)
    def _pending_committee(self):
        """
        User info accepted, need to select committee members
        """

    @transition(field=status, source=STATUS.PENDING_COMMITTEE, target=STATUS.COMMITTEE_REVIEW)
    def _to_committee(self):
        """
        Send report to committee
        """

    @transition(field=status, source=STATUS.COMMITTEE_REVIEW, target=STATUS.OSR_FINAL_REVIEW)
    def _committee_done(self):
        """
        Committee recommendation added
        """

    @transition(field=status, source=STATUS.COMMITTEE_REVIEW, target=STATUS.ACCEPTED)
    def _management_plan_done(self):
        """
        Waiting for committee management plan
        """
        
    @transition(field=status, source=STATUS.COMMITTEE_REVIEW, target=STATUS.CANT_MANAGE)
    def _cant_manage(self):
        """
        Unable to manage
        """

    @transition(field=status,
                source=[ STATUS.OSR_REVIEW,
                         STATUS.OSR_REVIEW_NO_CONFLICTS,
                         STATUS.COMMITTEE_MANAGEMENT ],
                target=STATUS.ACCEPTED)
    def _accept(self):
        """
        Submission processing done
        """
        self.date_resolved = datetime.now()

    def __unicode__(self):
        return "%s submitted on %s (%s)" % (self.report.user.user, self.date_submitted,self.get_status_display())
    
    class Meta:
        get_latest_by = 'date_submitted'


class IncomeConflict(models.Model):
    class INCOME:
        LOW = '0'
        MID = '2'
        MID_HIGH = '3'
        HIGH = '4'
        VERY_HIGH = '5'
        NOT_DETERMINABLE = '6'
        
    INCOME_CHOICES = ((INCOME.LOW, '$0-4,999'),
                      (INCOME.MID, '$5,000 - 9,999'),
                      (INCOME.MID_HIGH, '$10,000 - 19,000'),
                      (INCOME.HIGH, '$20,000 - 100,000'),
                      (INCOME.VERY_HIGH, 'Above $100,000'),
                      (INCOME.NOT_DETERMINABLE, 'The interest is one whose value cannot be readily determined through reference to public prices or other reasonable measures of fair market value.'))
        
    report = models.ForeignKey(AnnualReport)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    transferred = models.BooleanField()
    entity_name = models.CharField(max_length=250)
    
    estimated_income = models.CharField(max_length=1, choices=INCOME_CHOICES)
    income_by_twenty = models.DecimalField(decimal_places=2, max_digits=11,
        help_text="Enter the value as a decimal number without extra punctuation in multiples of $20,000: 60000.00", blank=True, null=True)
    income_by_fifty = models.DecimalField(decimal_places=2, max_digits=11,
        help_text="Enter the value as a decimal number without extra punctuation in multiples of $50,000: 150000.00", blank=True, null=True)

    is_univercity_sponsor = models.BooleanField()
    contribute = models.BooleanField()

    income_as_employee = models.BooleanField()
    income_honoraria = models.BooleanField()
    income_rice_ott_royalties = models.BooleanField()
    income_other_royalties = models.BooleanField()
    income_gift = models.BooleanField()
    income_endowment = models.BooleanField()
    income_dividends = models.BooleanField()
    income_loans = models.BooleanField()
    income_travel_funds = models.BooleanField()
    income_other = models.BooleanField()
    income_other_description = models.TextField(blank=True)
    
    have_sponsor_research = models.BooleanField()
    sponsor_research_description = models.TextField(blank=True)

    is_entity_interested = models.BooleanField()
    entity_interest_description = models.TextField(blank=True)

    have_gifts = models.BooleanField()
    gifts_description = models.TextField(blank=True)

    have_agreement = models.BooleanField()
    agreement_description = models.TextField(blank=True)

    have_employment = models.BooleanField()
    employement_description = models.TextField(blank=True)

    other_involved = models.BooleanField()
    involving_description = models.TextField(blank=True)
    
    existing_research_relation = models.BooleanField()
    existing_research_relation_description = models.TextField(blank=True)
    
    perceived_coi = models.BooleanField()
    perceived_coi_description = models.TextField(blank=True)
    
    additional_info = models.BooleanField()
    additional_info_description = models.TextField(blank=True)
    
    existing_management_plan = models.BooleanField()
    management_plan_description = models.TextField(blank=True)


    def __unicode__(self):
        return u"%s" % self.report.user 

class GiftConflict(models.Model):
    class INCOME:
        LOW = '0'
        MID = '2'
        MID_HIGH = '3'
        HIGH = '4'
        VERY_HIGH = '5'
        NOT_DETERMINABLE = '6'
        
    INCOME_CHOICES = ((INCOME.LOW, '$0-4,999'),
                      (INCOME.MID, '$5,000 - 9,999'),
                      (INCOME.MID_HIGH, '$10,000 - 19,000'),
                      (INCOME.HIGH, '$20,000 - 100,000'),
                      (INCOME.VERY_HIGH, 'Above $100,000'),
                      (INCOME.NOT_DETERMINABLE, 'The interest is one whose value cannot be readily determined through reference to public prices or other reasonable measures of fair market value.'))
        
    report = models.ForeignKey(AnnualReport)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    transferred = models.BooleanField()
    entity_name = models.CharField(max_length=250)
    
    estimated_income = models.CharField(max_length=1, choices=INCOME_CHOICES)
    income_by_twenty = models.DecimalField(decimal_places=2, max_digits=11,
        help_text="Enter the value as a decimal number without extra punctuation in multiples of $20,000: 60000.00", blank=True, null=True)
    income_by_fifty = models.DecimalField(decimal_places=2, max_digits=11,
        help_text="Enter the value as a decimal number without extra punctuation in multiples of $50,000: 150000.00", blank=True, null=True)

    is_univercity_sponsor = models.BooleanField()
    contribute = models.BooleanField()

    income_as_employee = models.BooleanField()
    income_honoraria = models.BooleanField()
    income_rice_ott_royalties = models.BooleanField()
    income_other_royalties = models.BooleanField()
    income_gift = models.BooleanField()
    income_endowment = models.BooleanField()
    income_dividends = models.BooleanField()
    income_loans = models.BooleanField()
    income_travel_funds = models.BooleanField()
    income_other = models.BooleanField()
    income_other_description = models.TextField(blank=True)
    
    have_sponsor_research = models.BooleanField()
    sponsor_research_description = models.TextField(blank=True)

    is_entity_interested = models.BooleanField()
    entity_interest_description = models.TextField(blank=True)

    have_gifts = models.BooleanField()
    gifts_description = models.TextField(blank=True)

    have_agreement = models.BooleanField()
    agreement_description = models.TextField(blank=True)

    have_employment = models.BooleanField()
    employement_description = models.TextField(blank=True)

    other_involved = models.BooleanField()
    involving_description = models.TextField(blank=True)
    
    existing_research_relation = models.BooleanField()
    existing_research_relation_description = models.TextField(blank=True)
    
    perceived_coi = models.BooleanField()
    perceived_coi_description = models.TextField(blank=True)
    
    additional_info = models.BooleanField()
    additional_info_description = models.TextField(blank=True)
    
    existing_management_plan = models.BooleanField()
    management_plan_description = models.TextField(blank=True)


    def __unicode__(self):
        return u"%s" % self.report.user

class BusinessConflict(models.Model):

    class VALUE:
        LOW = '0'
        MID = '2'
        MID_HIGH = '3'
        HIGH = '4'
        VERY_HIGH = '5'
        NOT_DETERMINABLE = '6'
        
    VALUE_CHOICES = ((VALUE.LOW, '$0-4,999'),
                      (VALUE.MID, '$5,000 - 9,999'),
                      (VALUE.MID_HIGH, '$10,000 - 19,000'),
                      (VALUE.HIGH, '$20,000 - 100,000'),
                      (VALUE.VERY_HIGH, 'Above $100,000'),
                      (VALUE.NOT_DETERMINABLE, 'The interest is one whose value cannot be readily determined through reference to public prices or other reasonable measures of fair market value.'))
                      
    class INTEREST:
        EQUITY = 'E'
        PARTNERSHIP = 'P'
        OTHER = 'O'
    INTEREST_CHOICES = ((INTEREST.EQUITY, 'Equity'),
                        (INTEREST.PARTNERSHIP, 'Partnership'),
                        (INTEREST.OTHER, 'Other'))

    report = models.ForeignKey(AnnualReport)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    transferred = models.BooleanField()
    entity_name = models.CharField(max_length=250)

    org_type = models.CharField(max_length=50)
    
    estimated_value = models.CharField(max_length=1, choices=VALUE_CHOICES)
    valuation_by_twenty = models.DecimalField(decimal_places=2, max_digits=11,
        help_text="Enter the value as a decimal number without extra punctuation in multiples of $20,000: 60000.00", blank=True, null=True)
    valuation_by_fifty = models.DecimalField(decimal_places=2, max_digits=11,
        help_text="Enter the value as a decimal number without extra punctuation in multiples of $50,000: 150000.00", blank=True, null=True)
        
    estimated_days_spent = models.CharField(max_length=250)

    ownership_pct = models.CharField(max_length=250)

    interest_type = models.CharField(max_length=1, choices=INTEREST_CHOICES)
    interest_description = models.TextField(blank=True)
    other_interest = models.TextField(blank=True)

    have_sponsor_research = models.BooleanField()
    sponsor_research_description = models.TextField(blank=True)

    is_entity_interested = models.BooleanField()
    entity_interest_description = models.TextField(blank=True)

    have_gifts = models.BooleanField()
    gifts_description = models.TextField(blank=True)

    have_agreement = models.BooleanField()
    agreement_description = models.TextField(blank=True)

    have_employment = models.BooleanField()
    employement_description = models.TextField(blank=True)

    other_involved = models.BooleanField()
    involving_description = models.TextField(blank=True)
    
    existing_research_relation = models.BooleanField()
    existing_research_relation_description = models.TextField(blank=True)
    
    perceived_coi = models.BooleanField()
    perceived_coi_description = models.TextField(blank=True)
    
    additional_info = models.BooleanField()
    additional_info_description = models.TextField(blank=True)

    existing_management_plan = models.BooleanField()
    management_plan_description = models.TextField(blank=True)

    rice_sponsor = models.BooleanField()
    rice_contributor = models.BooleanField()

    def __unicode__(self):
        return u"%s" % self.report.user 


class ConsultingConflict(models.Model):

    class INCOME:
        LOW = '0'
        MID = '2'
        MID_HIGH = '3'
        HIGH = '4'
        VERY_HIGH = '5'
        NOT_DETERMINABLE = '6'
        
    INCOME_CHOICES = ((INCOME.LOW, '$0-4,999'),
                      (INCOME.MID, '$5,000 - 9,999'),
                      (INCOME.MID_HIGH, '$10,000 - 19,000'),
                      (INCOME.HIGH, '$20,000 - 100,000'),
                      (INCOME.VERY_HIGH, 'Above $100,000'),
                      (INCOME.NOT_DETERMINABLE, 'The interest is one whose value cannot be readily determined through reference to public prices or other reasonable measures of fair market value.'))
                      
    report = models.ForeignKey(AnnualReport)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    transferred = models.BooleanField()
    entity_name = models.CharField(max_length=250)

    estimated_days_spent = models.CharField(max_length=250)
    estimated_income = models.CharField(max_length=1, choices=INCOME_CHOICES)
    income_by_twenty = models.DecimalField(decimal_places=2, max_digits=11,
        help_text="Enter the value as a decimal number without extra punctuation in multiples of $20,000: 60000.00", blank=True, null=True)
    income_by_fifty = models.DecimalField(decimal_places=2, max_digits=11,
        help_text="Enter the value as a decimal number without extra punctuation in multiples of $50,000: 150000.00", blank=True, null=True)

    rice_resources_use = models.BooleanField()

    rice_sponsor = models.BooleanField()
    rice_sponsor_description = models.TextField(blank=True)
    rice_contributor = models.BooleanField()
    rice_contributor_description = models.TextField(blank=True)

    other_involved = models.BooleanField()
    involving_description = models.TextField(blank=True)

    description = models.TextField()
    
    have_sponsor_research = models.BooleanField()
    sponsor_research_description = models.TextField(blank=True)

    is_entity_interested = models.BooleanField()
    entity_interest_description = models.TextField(blank=True)

    have_gifts = models.BooleanField()
    gifts_description = models.TextField(blank=True)

    have_agreement = models.BooleanField()
    agreement_description = models.TextField(blank=True)
    
    existing_research_relation = models.BooleanField()
    existing_research_relation_description = models.TextField(blank=True)
    
    perceived_coi = models.BooleanField()
    perceived_coi_description = models.TextField(blank=True)
    
    additional_info = models.BooleanField()
    additional_info_description = models.TextField(blank=True)
    
    existing_management_plan = models.BooleanField()
    management_plan_description = models.TextField(blank=True)



    def __unicode__(self):
        return u"%s" % self.report.user 


class TravelConflict(models.Model):
    report = models.ForeignKey(AnnualReport)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    transferred = models.BooleanField()
    sponsor = models.CharField(max_length=400)
    estimated_days_spent = models.CharField(max_length=100)
    destination = models.CharField(max_length=100)
    purpose = models.TextField()
    
    existing_research_relation = models.BooleanField()
    existing_research_relation_description = models.TextField(blank=True)

    def __unicode__(self):
        return u"%s" % self.report.user 

#
# Workflow data
#
class ActionLog(models.Model):
    class ACTION:
        SUBMIT = 'SMT'
        REJECT = 'RJT'
        ACKNOWLEDGE = 'AKN'
        APPROVE = 'APR'
        HAS_CONFLICT = 'CNF'
        REVISE = 'RVS'
        REVISED = 'RVD'
        PENDING_COMMITTEE = 'PCM'
        COMMITTEE_REVIEW = 'CRV'
        COMMITTEE_DONE = 'CMD'
        MANAGEMENT_PLAN = 'MGP'
        DONE_NO_CONFLICTS = 'DNC'
        DONE_WITH_MANAGEMENT_PLAN = 'DMP'
        DONE_CANT_BE_MANAGED = 'DCM'
    ACTION_CHOICES = ((ACTION.SUBMIT, 'Submitted'),
                      (ACTION.REJECT, 'Rejected'),
                      (ACTION.APPROVE, 'Approved'),
                      (ACTION.ACKNOWLEDGE, 'Acknowledged'),
                      (ACTION.HAS_CONFLICT, 'Has conflict'),
                      (ACTION.REVISE, 'Need additional info'),
                      (ACTION.REVISED, 'Additional info provided'),
                      (ACTION.PENDING_COMMITTEE, 'Pending Committee Assignment'),
                      (ACTION.COMMITTEE_REVIEW, 'Committee review in-progress'),
                      (ACTION.COMMITTEE_DONE, 'Committee done'),
                      (ACTION.MANAGEMENT_PLAN, 'Management plan required'),
                      (ACTION.DONE_NO_CONFLICTS, 'No conflicts'),
                      (ACTION.DONE_WITH_MANAGEMENT_PLAN, 'Resolved with management plan'),
                      (ACTION.DONE_CANT_BE_MANAGED, "Can't be managed"))

    submission = models.ForeignKey(ReportSubmission)
    sender = models.ForeignKey(UserProfile)
    action = models.CharField(max_length=3, choices=ACTION_CHOICES)
    text = models.TextField(blank=True, default="")
    private = models.TextField(blank=True, default="")
    sent = models.DateTimeField(auto_now_add=True)
    
    signature = models.CharField(max_length=250, default="", blank=True)

    class Meta:
        get_latest_by = 'sent'
    
    def __unicode__(self):
        return "%s" % self.action


class SupplementalInformation(models.Model):
    report = models.ForeignKey(AnnualReport)


class ReaderRecommendation(models.Model):
    report = models.ForeignKey(AnnualReport)
    reader = models.ForeignKey(UserProfile)


class Reminder(models.Model):
    sent = models.DateTimeField(auto_now_add=True)
    template = models.ForeignKey(EmailTemplate)
    sender = models.ForeignKey(UserProfile, blank=True, null=True)
    report = models.ForeignKey(AnnualReport)
    message = models.TextField(blank=True, default="")

    class Meta:
        get_latest_by = 'sent'

class CommitteeUpload(models.Model):
    member = models.ForeignKey(UserProfile)
    report = models.ForeignKey(AnnualReport)
    document = models.FileField(upload_to='committee/')

class ManagementPlan(models.Model):
    created_by = models.ForeignKey(UserProfile)
    report = models.ForeignKey(AnnualReport)
    plan = models.FileField(upload_to='management_plans/')
    
reversion.register(IncomeConflict)
reversion.register(GiftConflict)
reversion.register(BusinessConflict)
reversion.register(ConsultingConflict)
reversion.register(TravelConflict)
reversion.register(ReportSubmission)
reversion.register(AnnualReport)