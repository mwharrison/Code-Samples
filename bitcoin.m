///// This is the App Delegate for my Bitcoin app. It's a pretty crude implementation I used to get data from the API's, but then again, I am calling quite a few of them.


//
//  AppDelegate.m
//  Bitcoin Taskbar
//
//  Created by Michael Harrison on 11/1/13.
//  Copyright (c) 2013 Michael Harrison. All rights reserved.
//

#import "AppDelegate.h"
#import "Bitcoin.h"

@implementation AppDelegate

@synthesize updateTimer;
@synthesize bitcoinMenu;
@synthesize menuUpdated;
@synthesize menuExchange;

NSStatusItem *statusItem;


- (void)applicationDidFinishLaunching:(NSNotification *)aNotification
{
    NSString *locale =[[NSLocale currentLocale] localeIdentifier];
    if ([locale isEqualToString:@"en_US"]) {
        [self seUSDMtGox:self];
        [self.updateTimer invalidate];
        self.updateTimer = nil;
        self.updateTimer = [NSTimer scheduledTimerWithTimeInterval:60.0 target:self selector:@selector(seUSDMtGox:) userInfo:nil repeats:YES];
    }else if ([locale isEqualToString:@"en_GB"]) {
        [self seGBPMtGox:self];
        self.updateTimer = nil;
        [self.updateTimer invalidate];
        self.updateTimer = [NSTimer scheduledTimerWithTimeInterval:60.0 target:self selector:@selector(seUSDMtGox:) userInfo:nil repeats:YES];
    }else{
        [self seEURMtGox:self];
        [self.updateTimer invalidate];
        self.updateTimer = nil;
        self.updateTimer = [NSTimer scheduledTimerWithTimeInterval:60.0 target:self selector:@selector(seEURMtGox:) userInfo:nil repeats:YES];
    }
}

- (void) awakeFromNib
{
    NSString *version = [[NSBundle mainBundle] objectForInfoDictionaryKey:@"CFBundleVersion"];
    NSStatusBar *statusBar = [NSStatusBar systemStatusBar];
    statusItem = [statusBar statusItemWithLength:NSVariableStatusItemLength];
    [statusItem setHighlightMode:YES];
    [statusItem setMenu:bitcoinMenu];
    [statusItem setImage:[NSImage imageNamed:@"icon.png"]];
    [statusItem setToolTip:[NSString stringWithFormat:@"Bitcoin Toolbar v%@", version]];
}

- (void)updateBitcoinPrice:(NSString *)price
{
    NSDate* currentDate = [NSDate date];
    NSDateFormatter *dateFormatter = [[NSDateFormatter alloc] init];
    [dateFormatter setDateFormat:@"HH:mm:ss 'on' dd MMM"];
    NSString *formattedDateString = [dateFormatter stringFromDate:currentDate];
    
    [self.menuUpdated setTitle:[NSString stringWithFormat:@"Last Update: %@", formattedDateString]];
    [statusItem setTitle:[NSString stringWithFormat:@"%@", price]];
}

- (IBAction)viewChart:(id)sender {
    NSString *selected_exchange = [NSString stringWithFormat:@"%@", self.menuExchange.title];
    if ([selected_exchange isEqualToString:@"Exchange: MtGox(USD)"])
    {
        [[NSWorkspace sharedWorkspace] openURL:[NSURL URLWithString:@"http://bitcoincharts.com/charts/mtgoxUSD"]];
    } else if ([selected_exchange isEqualToString:@"Exchange: MtGox(GBP)"]) {
        [[NSWorkspace sharedWorkspace] openURL:[NSURL URLWithString:@"http://bitcoincharts.com/charts/mtgoxGBP"]];
    } else if ([selected_exchange isEqualToString:@"Exchange: MtGox(EUR)"]) {
        [[NSWorkspace sharedWorkspace] openURL:[NSURL URLWithString:@"http://bitcoincharts.com/charts/mtgoxEUR"]];
    } else if ([selected_exchange isEqualToString:@"Exchange: MtGox(CHF)"]) {
        [[NSWorkspace sharedWorkspace] openURL:[NSURL URLWithString:@"http://bitcoincharts.com/charts/mtgoxCHF"]];
    } else if ([selected_exchange isEqualToString:@"Exchange: MtGox(RUB)"]) {
        [[NSWorkspace sharedWorkspace] openURL:[NSURL URLWithString:@"http://bitcoincharts.com/charts/mtgoxRUB"]];
    } else if ([selected_exchange isEqualToString:@"Exchange: MtGox(JPY)"]) {
        [[NSWorkspace sharedWorkspace] openURL:[NSURL URLWithString:@"http://bitcoincharts.com/charts/mtgoxJPY"]];
    } else if ([selected_exchange isEqualToString:@"Exchange: MtGox(AUD)"]) {
        [[NSWorkspace sharedWorkspace] openURL:[NSURL URLWithString:@"http://bitcoincharts.com/charts/mtgoxAUD"]];
    } else if ([selected_exchange isEqualToString:@"Exchange: MtGox(CAD)"]) {
        [[NSWorkspace sharedWorkspace] openURL:[NSURL URLWithString:@"http://bitcoincharts.com/charts/mtgoxCAD"]];
    } else if ([selected_exchange isEqualToString:@"Exchange: Coinbase(USD)"]) {
        [[NSWorkspace sharedWorkspace] openURL:[NSURL URLWithString:@"https://coinbase.com/charts"]];
    } else if ([selected_exchange isEqualToString:@"Exchange: Coinbase(GBP)"]) {
        [[NSWorkspace sharedWorkspace] openURL:[NSURL URLWithString:@"https://coinbase.com/charts"]];
    } else if ([selected_exchange isEqualToString:@"Exchange: Coinbase(EUR)"]) {
        [[NSWorkspace sharedWorkspace] openURL:[NSURL URLWithString:@"https://coinbase.com/charts"]];
    } else if ([selected_exchange isEqualToString:@"Exchange: Vircurex(USD)"]) {
        [[NSWorkspace sharedWorkspace] openURL:[NSURL URLWithString:@"http://bitcoincharts.com/charts/vcxUSD"]];
    } else if ([selected_exchange isEqualToString:@"Exchange: Vircurex(EUR)"]) {
        [[NSWorkspace sharedWorkspace] openURL:[NSURL URLWithString:@"http://bitcoincharts.com/charts/vcxEUR"]];
    } else if ([selected_exchange isEqualToString:@"Exchange: Local Bitcoins(USD)"]) {
        [[NSWorkspace sharedWorkspace] openURL:[NSURL URLWithString:@"http://bitcoincharts.com/charts/localbtcUSD"]];
    } else if ([selected_exchange isEqualToString:@"Exchange: Local Bitcoins(GBP)"]) {
        [[NSWorkspace sharedWorkspace] openURL:[NSURL URLWithString:@"http://bitcoincharts.com/charts/localbtcGBP"]];
    } else if ([selected_exchange isEqualToString:@"Exchange: Local Bitcoins(EUR)"]) {
        [[NSWorkspace sharedWorkspace] openURL:[NSURL URLWithString:@"http://bitcoincharts.com/charts/localbtcEUR"]];
    } else if ([selected_exchange isEqualToString:@"Exchange: CampBX(USD)"]) {
        [[NSWorkspace sharedWorkspace] openURL:[NSURL URLWithString:@"http://bitcoincharts.com/charts/cbxUSD"]];
    } else if ([selected_exchange isEqualToString:@"Exchange: Bitstamp(USD)"]) {
        [[NSWorkspace sharedWorkspace] openURL:[NSURL URLWithString:@"http://bitcoincharts.com/charts/bitstampUSD"]];
    } else if ([selected_exchange isEqualToString:@"Exchange: Kraken(USD)"]) {
        [[NSWorkspace sharedWorkspace] openURL:[NSURL URLWithString:@"https://www.kraken.com/market"]];
    } else if ([selected_exchange isEqualToString:@"Exchange: Kraken(EUR)"]) {
        [[NSWorkspace sharedWorkspace] openURL:[NSURL URLWithString:@"https://www.kraken.com/market?pair=XXBTZEUR"]];
    } else {
        NSAlert *alert = [[NSAlert alloc] init];
        [alert addButtonWithTitle:@"OK"];
        [alert setMessageText:@"No exchange chart found!"];
        [alert setInformativeText:@"This exchange does not have a chart associated with it at this time."];
        [alert setAlertStyle:NSWarningAlertStyle];
        [alert runModal];
    }
}

- (IBAction)menuRefresh:(id)sender {
    [self.updateTimer fire];
}

- (IBAction)seUSDBitpay:(id)sender {
    NSString *str=@"https://bitpay.com/api/rates";
    [self.menuExchange setTitle:[NSString stringWithFormat:@"Exchange: Bitpay(USD)"]];
    NSURL *url=[NSURL URLWithString:str];
    NSData *data=[NSData dataWithContentsOfURL:url];
    NSError *error=nil;
    id response=[NSJSONSerialization JSONObjectWithData:data options:
                 NSJSONReadingMutableContainers error:&error];
    NSDictionary *exchange_return = [response objectAtIndex:0];
    float price = [[exchange_return objectForKey:@"rate"] floatValue];
    NSString *readable_price = [NSString stringWithFormat:@"$%.2f", price];
    [self updateBitcoinPrice:readable_price];
    [self.updateTimer invalidate];
    self.updateTimer = nil;
    self.updateTimer = [NSTimer scheduledTimerWithTimeInterval:60.0 target:self selector:@selector(seUSDBitpay:) userInfo:nil repeats:YES];
}

- (IBAction)seGBPBitpay:(id)sender {
    NSString *str=@"https://bitpay.com/api/rates";
    [self.menuExchange setTitle:[NSString stringWithFormat:@"Exchange: Bitpay(GBP)"]];
    NSURL *url=[NSURL URLWithString:str];
    NSData *data=[NSData dataWithContentsOfURL:url];
    NSError *error=nil;
    id response=[NSJSONSerialization JSONObjectWithData:data options:
                 NSJSONReadingMutableContainers error:&error];
    NSDictionary *exchange_return = [response objectAtIndex:2];
    float price = [[exchange_return objectForKey:@"rate"] floatValue];
    NSString *readable_price = [NSString stringWithFormat:@"£%.2f", price];
    [self updateBitcoinPrice:readable_price];
    [self.updateTimer invalidate];
    self.updateTimer = nil;
    self.updateTimer = [NSTimer scheduledTimerWithTimeInterval:60.0 target:self selector:@selector(seGBPBitpay:) userInfo:nil repeats:YES];
}

- (IBAction)seEURBitpay:(id)sender {
    NSString *str=@"https://bitpay.com/api/rates";
    [self.menuExchange setTitle:[NSString stringWithFormat:@"Exchange: Bitpay(EUR)"]];
    NSURL *url=[NSURL URLWithString:str];
    NSData *data=[NSData dataWithContentsOfURL:url];
    NSError *error=nil;
    id response=[NSJSONSerialization JSONObjectWithData:data options:
                 NSJSONReadingMutableContainers error:&error];
    NSDictionary *exchange_return = [response objectAtIndex:1];
    float price = [[exchange_return objectForKey:@"rate"] floatValue];
    NSString *readable_price = [NSString stringWithFormat:@"€%.2f", price];
    [self updateBitcoinPrice:readable_price];
    [self.updateTimer invalidate];
    self.updateTimer = nil;
    self.updateTimer = [NSTimer scheduledTimerWithTimeInterval:60.0 target:self selector:@selector(seEURBitpay:) userInfo:nil repeats:YES];
}

- (IBAction)seUSDCoinbase:(id)sender {
    NSString *str=@"https://coinbase.com/api/v1/currencies/exchange_rates";
    [self.menuExchange setTitle:[NSString stringWithFormat:@"Exchange: Coinbase(USD)"]];
    NSURL *url=[NSURL URLWithString:str];
    NSData *data=[NSData dataWithContentsOfURL:url];
    NSError *error=nil;
    id response=[NSJSONSerialization JSONObjectWithData:data options:
                 NSJSONReadingMutableContainers error:&error];
    float price = [[response objectForKey:@"btc_to_usd"] floatValue];
    NSString *readable_price = [NSString stringWithFormat:@"$%.2f", price];
    [self updateBitcoinPrice:readable_price];
    [self.updateTimer invalidate];
    self.updateTimer = nil;
    self.updateTimer = [NSTimer scheduledTimerWithTimeInterval:60.0 target:self selector:@selector(seUSDCoinbase:) userInfo:nil repeats:YES];
}

- (IBAction)seGBPCoinbase:(id)sender {
    NSString *str=@"https://coinbase.com/api/v1/currencies/exchange_rates";
    [self.menuExchange setTitle:[NSString stringWithFormat:@"Exchange: Coinbase(GBP)"]];
    NSURL *url=[NSURL URLWithString:str];
    NSData *data=[NSData dataWithContentsOfURL:url];
    NSError *error=nil;
    id response=[NSJSONSerialization JSONObjectWithData:data options:
                 NSJSONReadingMutableContainers error:&error];
    float price = [[response objectForKey:@"btc_to_gbp"] floatValue];
    NSString *readable_price = [NSString stringWithFormat:@"£%.2f", price];
    [self updateBitcoinPrice:readable_price];
    [self.updateTimer invalidate];
    self.updateTimer = nil;
    self.updateTimer = [NSTimer scheduledTimerWithTimeInterval:60.0 target:self selector:@selector(seGBPCoinbase:) userInfo:nil repeats:YES];
}

- (IBAction)seEURCoinbase:(id)sender {
    NSString *str=@"https://coinbase.com/api/v1/currencies/exchange_rates";
    [self.menuExchange setTitle:[NSString stringWithFormat:@"Exchange: Coinbase(EUR)"]];
    NSURL *url=[NSURL URLWithString:str];
    NSData *data=[NSData dataWithContentsOfURL:url];
    NSError *error=nil;
    id response=[NSJSONSerialization JSONObjectWithData:data options:
                 NSJSONReadingMutableContainers error:&error];
    float price = [[response objectForKey:@"btc_to_eur"] floatValue];
    NSString *readable_price = [NSString stringWithFormat:@"€%.2f", price];
    [self updateBitcoinPrice:readable_price];
    [self.updateTimer invalidate];
    self.updateTimer = nil;
    self.updateTimer = [NSTimer scheduledTimerWithTimeInterval:60.0 target:self selector:@selector(seEURCoinbase:) userInfo:nil repeats:YES];
}

- (IBAction)seUSDVircurex:(id)sender {
    NSString *str=@"https://vircurex.com/api/get_info_for_currency.json";
    [self.menuExchange setTitle:[NSString stringWithFormat:@"Exchange: Vircurex(USD)"]];
    NSURL *url=[NSURL URLWithString:str];
    NSData *data=[NSData dataWithContentsOfURL:url];
    NSError *error=nil;
    id response=[NSJSONSerialization JSONObjectWithData:data options:
                 NSJSONReadingMutableContainers error:&error];
    NSDictionary *exchange_return = [response objectForKey:@"BTC"];
    NSDictionary *usd = [exchange_return objectForKey:@"USD"];
    float price = [[usd objectForKey:@"last_trade"] floatValue];
    NSString *readable_price = [NSString stringWithFormat:@"$%.2f", price];
    [self updateBitcoinPrice:readable_price];
    [self.updateTimer invalidate];
    self.updateTimer = nil;
    self.updateTimer = [NSTimer scheduledTimerWithTimeInterval:60.0 target:self selector:@selector(seUSDVircurex:) userInfo:nil repeats:YES];
}

- (IBAction)seEURVircurex:(id)sender {
    NSString *str=@"https://vircurex.com/api/get_info_for_currency.json";
    [self.menuExchange setTitle:[NSString stringWithFormat:@"Exchange: Vircurex(EUR)"]];
    NSURL *url=[NSURL URLWithString:str];
    NSData *data=[NSData dataWithContentsOfURL:url];
    NSError *error=nil;
    id response=[NSJSONSerialization JSONObjectWithData:data options:
                 NSJSONReadingMutableContainers error:&error];
    NSDictionary *exchange_return = [response objectForKey:@"BTC"];
    NSDictionary *usd = [exchange_return objectForKey:@"EUR"];
    float price = [[usd objectForKey:@"last_trade"] floatValue];
    NSString *readable_price = [NSString stringWithFormat:@"€%.2f", price];
    [self updateBitcoinPrice:readable_price];
    [self.updateTimer invalidate];
    self.updateTimer = nil;
    self.updateTimer = [NSTimer scheduledTimerWithTimeInterval:60.0 target:self selector:@selector(seEURVircurex:) userInfo:nil repeats:YES];
}

- (IBAction)seUSDLocalBitcoins:(id)sender {
    NSString *str2=@"https://localbitcoins.com/bitcoinaverage/ticker-all-currencies/";
     [self.menuExchange setTitle:[NSString stringWithFormat:@"Exchange: Local Bitcoins(USD)"]];
     NSURL *url=[NSURL URLWithString:str2];
     NSData *data=[NSData dataWithContentsOfURL:url];
     NSError *error=nil;
     id response=[NSJSONSerialization JSONObjectWithData:data options:
     NSJSONReadingMutableContainers error:&error];
     NSDictionary *exchange_return = [response objectForKey:@"USD"];
     NSDictionary *rates = [exchange_return objectForKey:@"rates"];
    float price = [[rates objectForKey:@"last"] floatValue];
    NSString *readable_price = [NSString stringWithFormat:@"$%.2f", price];
    [self updateBitcoinPrice:readable_price];
    [self.updateTimer invalidate];
    self.updateTimer = nil;
    self.updateTimer = [NSTimer scheduledTimerWithTimeInterval:60.0 target:self selector:@selector(seUSDLocalBitcoins:) userInfo:nil repeats:YES];
    
}

- (IBAction)seGBPLocalBitcoins:(id)sender {
    NSString *str2=@"https://localbitcoins.com/bitcoinaverage/ticker-all-currencies/";
    [self.menuExchange setTitle:[NSString stringWithFormat:@"Exchange: Local Bitcoins(GBP)"]];
    NSURL *url=[NSURL URLWithString:str2];
    NSData *data=[NSData dataWithContentsOfURL:url];
    NSError *error=nil;
    id response=[NSJSONSerialization JSONObjectWithData:data options:
                 NSJSONReadingMutableContainers error:&error];
    NSDictionary *exchange_return = [response objectForKey:@"GBP"];
    NSDictionary *rates = [exchange_return objectForKey:@"rates"];
    float price = [[rates objectForKey:@"last"] floatValue];
    NSString *readable_price = [NSString stringWithFormat:@"£%.2f", price];
    [self updateBitcoinPrice:readable_price];
    [self.updateTimer invalidate];
    self.updateTimer = nil;
    self.updateTimer = [NSTimer scheduledTimerWithTimeInterval:60.0 target:self selector:@selector(seGBPLocalBitcoins:) userInfo:nil repeats:YES];
}

- (IBAction)seEURLocalBitcoins:(id)sender {
    NSString *str2=@"https://localbitcoins.com/bitcoinaverage/ticker-all-currencies/";
    [self.menuExchange setTitle:[NSString stringWithFormat:@"Exchange: Local Bitcoins(EUR)"]];
    NSURL *url=[NSURL URLWithString:str2];
    NSData *data=[NSData dataWithContentsOfURL:url];
    NSError *error=nil;
    id response=[NSJSONSerialization JSONObjectWithData:data options:
                 NSJSONReadingMutableContainers error:&error];
    NSDictionary *exchange_return = [response objectForKey:@"EUR"];
    NSDictionary *rates = [exchange_return objectForKey:@"rates"];
    float price = [[rates objectForKey:@"last"] floatValue];
    NSString *readable_price = [NSString stringWithFormat:@"€%.2f", price];
    [self updateBitcoinPrice:readable_price];
    [self.updateTimer invalidate];
    self.updateTimer = nil;
    self.updateTimer = [NSTimer scheduledTimerWithTimeInterval:60.0 target:self selector:@selector(seEURLocalBitcoins:) userInfo:nil repeats:YES];
}

- (IBAction)seCHFLocalBitcoins:(id)sender {
    NSString *str2=@"https://localbitcoins.com/bitcoinaverage/ticker-all-currencies/";
    [self.menuExchange setTitle:[NSString stringWithFormat:@"Exchange: Local Bitcoins(CHF)"]];
    NSURL *url=[NSURL URLWithString:str2];
    NSData *data=[NSData dataWithContentsOfURL:url];
    NSError *error=nil;
    id response=[NSJSONSerialization JSONObjectWithData:data options:
                 NSJSONReadingMutableContainers error:&error];
    NSDictionary *exchange_return = [response objectForKey:@"CHF"];
    NSDictionary *rates = [exchange_return objectForKey:@"rates"];
    float price = [[rates objectForKey:@"last"] floatValue];
    NSString *readable_price = [NSString stringWithFormat:@"₣%.2f", price];
    [self updateBitcoinPrice:readable_price];
    [self.updateTimer invalidate];
    self.updateTimer = nil;
    self.updateTimer = [NSTimer scheduledTimerWithTimeInterval:60.0 target:self selector:@selector(seCHFLocalBitcoins:) userInfo:nil repeats:YES];
}

- (IBAction)seRUBLocalBitcoins:(id)sender {
    NSString *str2=@"https://localbitcoins.com/bitcoinaverage/ticker-all-currencies/";
    [self.menuExchange setTitle:[NSString stringWithFormat:@"Exchange: Local Bitcoins(RUB)"]];
    NSURL *url=[NSURL URLWithString:str2];
    NSData *data=[NSData dataWithContentsOfURL:url];
    NSError *error=nil;
    id response=[NSJSONSerialization JSONObjectWithData:data options:
                 NSJSONReadingMutableContainers error:&error];
    NSDictionary *exchange_return = [response objectForKey:@"RUB"];
    NSDictionary *rates = [exchange_return objectForKey:@"rates"];
    float price = [[rates objectForKey:@"last"] floatValue];
    NSString *readable_price = [NSString stringWithFormat:@"руб%.2f", price];
    [self updateBitcoinPrice:readable_price];
    [self.updateTimer invalidate];
    self.updateTimer = nil;
    self.updateTimer = [NSTimer scheduledTimerWithTimeInterval:60.0 target:self selector:@selector(seRUBLocalBitcoins:) userInfo:nil repeats:YES];
}

- (IBAction)seJPYLocalBitcoins:(id)sender {
    NSString *str2=@"https://localbitcoins.com/bitcoinaverage/ticker-all-currencies/";
    [self.menuExchange setTitle:[NSString stringWithFormat:@"Exchange: Local Bitcoins(JPY)"]];
    NSURL *url=[NSURL URLWithString:str2];
    NSData *data=[NSData dataWithContentsOfURL:url];
    NSError *error=nil;
    id response=[NSJSONSerialization JSONObjectWithData:data options:
                 NSJSONReadingMutableContainers error:&error];
    NSDictionary *exchange_return = [response objectForKey:@"JPY"];
    NSDictionary *rates = [exchange_return objectForKey:@"rates"];
    float price = [[rates objectForKey:@"last"] floatValue];
    NSString *readable_price = [NSString stringWithFormat:@"¥%.2f", price];
    [self updateBitcoinPrice:readable_price];
    [self.updateTimer invalidate];
    self.updateTimer = nil;
    self.updateTimer = [NSTimer scheduledTimerWithTimeInterval:60.0 target:self selector:@selector(seJPYLocalBitcoins:) userInfo:nil repeats:YES];
}

- (IBAction)seAUDLocalBitcoins:(id)sender {
    NSString *str2=@"https://localbitcoins.com/bitcoinaverage/ticker-all-currencies/";
    [self.menuExchange setTitle:[NSString stringWithFormat:@"Exchange: Local Bitcoins(AUD)"]];
    NSURL *url=[NSURL URLWithString:str2];
    NSData *data=[NSData dataWithContentsOfURL:url];
    NSError *error=nil;
    id response=[NSJSONSerialization JSONObjectWithData:data options:
                 NSJSONReadingMutableContainers error:&error];
    NSDictionary *exchange_return = [response objectForKey:@"AUD"];
    NSDictionary *rates = [exchange_return objectForKey:@"rates"];
    float price = [[rates objectForKey:@"last"] floatValue];
    NSString *readable_price = [NSString stringWithFormat:@"$%.2f", price];
    [self updateBitcoinPrice:readable_price];
    [self.updateTimer invalidate];
    self.updateTimer = nil;
    self.updateTimer = [NSTimer scheduledTimerWithTimeInterval:60.0 target:self selector:@selector(seAUDLocalBitcoins:) userInfo:nil repeats:YES];
}

- (IBAction)seCADLocalBitcoins:(id)sender {
    NSString *str2=@"https://localbitcoins.com/bitcoinaverage/ticker-all-currencies/";
    [self.menuExchange setTitle:[NSString stringWithFormat:@"Exchange: Local Bitcoins(CAD)"]];
    NSURL *url=[NSURL URLWithString:str2];
    NSData *data=[NSData dataWithContentsOfURL:url];
    NSError *error=nil;
    id response=[NSJSONSerialization JSONObjectWithData:data options:
                 NSJSONReadingMutableContainers error:&error];
    NSDictionary *exchange_return = [response objectForKey:@"CAD"];
    NSDictionary *rates = [exchange_return objectForKey:@"rates"];
    float price = [[rates objectForKey:@"last"] floatValue];
    NSString *readable_price = [NSString stringWithFormat:@"$%.2f", price];
    [self updateBitcoinPrice:readable_price];
    [self.updateTimer invalidate];
    self.updateTimer = nil;
    self.updateTimer = [NSTimer scheduledTimerWithTimeInterval:60.0 target:self selector:@selector(seCADLocalBitcoins:) userInfo:nil repeats:YES];
}

- (IBAction)seUSDKraken:(id)sender {
    NSString *str=@"https://api.kraken.com/0/public/Ticker?pair=XXBTZUSD";
    [self.menuExchange setTitle:[NSString stringWithFormat:@"Exchange: Kraken(USD)"]];
    
    NSURL *url=[NSURL URLWithString:str];
    NSData *data=[NSData dataWithContentsOfURL:url];
    NSError *error=nil;
    id response=[NSJSONSerialization JSONObjectWithData:data options:
                 NSJSONReadingMutableContainers error:&error];
    NSDictionary *result = [response objectForKey:@"result"];
    NSDictionary *last = [result objectForKey:@"XXBTZUSD"];
    NSArray *c = [last objectForKey:@"c"];
    float price = [[c objectAtIndex: 0] floatValue];
    NSString *readable_price = [NSString stringWithFormat:@"$%.2f", price];
    [self updateBitcoinPrice:readable_price];
    [self.updateTimer invalidate];
    self.updateTimer = nil;
    self.updateTimer = [NSTimer scheduledTimerWithTimeInterval:60.0 target:self selector:@selector(seUSDKraken:) userInfo:nil repeats:YES];
}

- (IBAction)seEURKracken:(id)sender {
    NSString *str=@"https://api.kraken.com/0/public/Ticker?pair=XXBTZEUR";
    [self.menuExchange setTitle:[NSString stringWithFormat:@"Exchange: Kraken(EUR)"]];
    
    NSURL *url=[NSURL URLWithString:str];
    NSData *data=[NSData dataWithContentsOfURL:url];
    NSError *error=nil;
    id response=[NSJSONSerialization JSONObjectWithData:data options:
                 NSJSONReadingMutableContainers error:&error];
    NSDictionary *result = [response objectForKey:@"result"];
    NSDictionary *last = [result objectForKey:@"XXBTZEUR"];
    NSArray *c = [last objectForKey:@"c"];
    float price = [[c objectAtIndex: 0] floatValue];
    NSString *readable_price = [NSString stringWithFormat:@"€%.2f", price];
    [self updateBitcoinPrice:readable_price];
    [self.updateTimer invalidate];
    self.updateTimer = nil;
    self.updateTimer = [NSTimer scheduledTimerWithTimeInterval:60.0 target:self selector:@selector(seEURKracken:) userInfo:nil repeats:YES];
}


- (IBAction)seUSDMtGox:(id)sender {
    NSString *str=@"https://mtgox.com/api/1/BTCUSD/ticker";
    [self.menuExchange setTitle:[NSString stringWithFormat:@"Exchange: MtGox(USD)"]];
    
    NSURL *url=[NSURL URLWithString:str];
    NSData *data=[NSData dataWithContentsOfURL:url];
    NSError *error=nil;
    id response=[NSJSONSerialization JSONObjectWithData:data options:
                 NSJSONReadingMutableContainers error:&error];
    NSDictionary *mtgox_return = [response objectForKey:@"return"];
    NSDictionary *last = [mtgox_return objectForKey:@"last"];
    float price = [[last objectForKey:@"value"] floatValue];
    NSString *readable_price = [NSString stringWithFormat:@"$%.2f", price];
    [self updateBitcoinPrice:readable_price];
    [self.updateTimer invalidate];
    self.updateTimer = nil;
    self.updateTimer = [NSTimer scheduledTimerWithTimeInterval:60.0 target:self selector:@selector(seUSDMtGox:) userInfo:nil repeats:YES];
    
}

- (IBAction)seGBPMtGox:(id)sender {
    NSString *str=@"https://mtgox.com/api/1/BTCGBP/ticker";
    [self.menuExchange setTitle:[NSString stringWithFormat:@"Exchange: MtGox(GBP)"]];
    NSURL *url=[NSURL URLWithString:str];
    NSData *data=[NSData dataWithContentsOfURL:url];
    NSError *error=nil;
    id response=[NSJSONSerialization JSONObjectWithData:data options:
                 NSJSONReadingMutableContainers error:&error];
    NSDictionary *mtgox_return = [response objectForKey:@"return"];
    NSDictionary *last = [mtgox_return objectForKey:@"last"];
    float price = [[last objectForKey:@"value"] floatValue];
    NSString *readable_price = [NSString stringWithFormat:@"£%.2f", price];
    [self updateBitcoinPrice:readable_price];
    [self.updateTimer invalidate];
    self.updateTimer = nil;
    self.updateTimer = [NSTimer scheduledTimerWithTimeInterval:60.0 target:self selector:@selector(seGBPMtGox:) userInfo:nil repeats:YES];
}

- (IBAction)seEURMtGox:(id)sender {
    NSString *str=@"https://mtgox.com/api/1/BTCEUR/ticker";
    [self.menuExchange setTitle:[NSString stringWithFormat:@"Exchange: MtGox(EUR)"]];
    NSURL *url=[NSURL URLWithString:str];
    NSData *data=[NSData dataWithContentsOfURL:url];
    NSError *error=nil;
    id response=[NSJSONSerialization JSONObjectWithData:data options:
                 NSJSONReadingMutableContainers error:&error];
    NSDictionary *mtgox_return = [response objectForKey:@"return"];
    NSDictionary *last = [mtgox_return objectForKey:@"last"];
    float price = [[last objectForKey:@"value"] floatValue];
    NSString *readable_price = [NSString stringWithFormat:@"€%.2f", price];
    [self updateBitcoinPrice:readable_price];
    [self.updateTimer invalidate];
    self.updateTimer = nil;
    self.updateTimer = [NSTimer scheduledTimerWithTimeInterval:60.0 target:self selector:@selector(seEURMtGox:) userInfo:nil repeats:YES];
}

- (IBAction)seCHFMtGox:(id)sender {
    NSString *str=@"https://mtgox.com/api/1/BTCCHF/ticker";
    [self.menuExchange setTitle:[NSString stringWithFormat:@"Exchange: MtGox(CHF)"]];
    NSURL *url=[NSURL URLWithString:str];
    NSData *data=[NSData dataWithContentsOfURL:url];
    NSError *error=nil;
    id response=[NSJSONSerialization JSONObjectWithData:data options:
                 NSJSONReadingMutableContainers error:&error];
    NSDictionary *mtgox_return = [response objectForKey:@"return"];
    NSDictionary *last = [mtgox_return objectForKey:@"last"];
    float price = [[last objectForKey:@"value"] floatValue];
    NSString *readable_price = [NSString stringWithFormat:@"₣%.2f", price];
    [self updateBitcoinPrice:readable_price];
    [self.updateTimer invalidate];
    self.updateTimer = nil;
    self.updateTimer = [NSTimer scheduledTimerWithTimeInterval:60.0 target:self selector:@selector(seCHFMtGox:) userInfo:nil repeats:YES];
}

- (IBAction)seRUBMtGox:(id)sender {
    NSString *str=@"https://mtgox.com/api/1/BTCRUB/ticker";
    [self.menuExchange setTitle:[NSString stringWithFormat:@"Exchange: MtGox(RUB)"]];
    NSURL *url=[NSURL URLWithString:str];
    NSData *data=[NSData dataWithContentsOfURL:url];
    NSError *error=nil;
    id response=[NSJSONSerialization JSONObjectWithData:data options:
                 NSJSONReadingMutableContainers error:&error];
    NSDictionary *mtgox_return = [response objectForKey:@"return"];
    NSDictionary *last = [mtgox_return objectForKey:@"last"];
    float price = [[last objectForKey:@"value"] floatValue];
    NSString *readable_price = [NSString stringWithFormat:@"руб%.2f", price];
    [self updateBitcoinPrice:readable_price];
    [self.updateTimer invalidate];
    self.updateTimer = nil;
    self.updateTimer = [NSTimer scheduledTimerWithTimeInterval:60.0 target:self selector:@selector(seRUBMtGox:) userInfo:nil repeats:YES];
}

- (IBAction)seJPYMtGox:(id)sender {
    NSString *str=@"https://mtgox.com/api/1/BTCJPY/ticker";
    [self.menuExchange setTitle:[NSString stringWithFormat:@"Exchange: MtGox(JPY)"]];
    NSURL *url=[NSURL URLWithString:str];
    NSData *data=[NSData dataWithContentsOfURL:url];
    NSError *error=nil;
    id response=[NSJSONSerialization JSONObjectWithData:data options:
                 NSJSONReadingMutableContainers error:&error];
    NSDictionary *mtgox_return = [response objectForKey:@"return"];
    NSDictionary *last = [mtgox_return objectForKey:@"last"];
    float price = [[last objectForKey:@"value"] floatValue];
    NSString *readable_price = [NSString stringWithFormat:@"¥%.2f", price];
    [self updateBitcoinPrice:readable_price];
    [self.updateTimer invalidate];
    self.updateTimer = nil;
    self.updateTimer = [NSTimer scheduledTimerWithTimeInterval:60.0 target:self selector:@selector(seJPYMtGox:) userInfo:nil repeats:YES];
}

- (IBAction)seAUDMtGox:(id)sender {
    NSString *str=@"https://mtgox.com/api/1/BTCAUD/ticker";
    [self.menuExchange setTitle:[NSString stringWithFormat:@"Exchange: MtGox(AUD)"]];
    NSURL *url=[NSURL URLWithString:str];
    NSData *data=[NSData dataWithContentsOfURL:url];
    NSError *error=nil;
    id response=[NSJSONSerialization JSONObjectWithData:data options:
                 NSJSONReadingMutableContainers error:&error];
    NSDictionary *mtgox_return = [response objectForKey:@"return"];
    NSDictionary *last = [mtgox_return objectForKey:@"last"];
    float price = [[last objectForKey:@"value"] floatValue];
    NSString *readable_price = [NSString stringWithFormat:@"$%.2f", price];
    [self updateBitcoinPrice:readable_price];
    [self.updateTimer invalidate];
    self.updateTimer = nil;
    self.updateTimer = [NSTimer scheduledTimerWithTimeInterval:60.0 target:self selector:@selector(seAUDMtGox:) userInfo:nil repeats:YES];
}

- (IBAction)seCADMtGox:(id)sender {
    NSString *str=@"https://mtgox.com/api/1/BTCCAD/ticker";
    [self.menuExchange setTitle:[NSString stringWithFormat:@"Exchange: MtGox(CAD)"]];
    NSURL *url=[NSURL URLWithString:str];
    NSData *data=[NSData dataWithContentsOfURL:url];
    NSError *error=nil;
    id response=[NSJSONSerialization JSONObjectWithData:data options:
                 NSJSONReadingMutableContainers error:&error];
    NSDictionary *mtgox_return = [response objectForKey:@"return"];
    NSDictionary *last = [mtgox_return objectForKey:@"last"];
    float price = [[last objectForKey:@"value"] floatValue];
    NSString *readable_price = [NSString stringWithFormat:@"$%.2f", price];
    [self updateBitcoinPrice:readable_price];
    [self.updateTimer invalidate];
    self.updateTimer = nil;
    self.updateTimer = [NSTimer scheduledTimerWithTimeInterval:60.0 target:self selector:@selector(seCADMtGox:) userInfo:nil repeats:YES];
}

- (IBAction)seUSDCampBX:(id)sender {
    NSString *str=@"http://campbx.com/api/xticker.php";
    [self.menuExchange setTitle:[NSString stringWithFormat:@"Exchange: CampBX(USD)"]];
    NSURL *url=[NSURL URLWithString:str];
    NSData *data=[NSData dataWithContentsOfURL:url];
    NSError *error=nil;
    id response=[NSJSONSerialization JSONObjectWithData:data options:
                 NSJSONReadingMutableContainers error:&error];
    float price = [[response objectForKey:@"Last Trade"] floatValue];
    NSString *readable_price = [NSString stringWithFormat:@"$%.2f", price];
    [self updateBitcoinPrice:readable_price];
    [self.updateTimer invalidate];
    self.updateTimer = nil;
    self.updateTimer = [NSTimer scheduledTimerWithTimeInterval:60.0 target:self selector:@selector(seUSDCampBX:) userInfo:nil repeats:YES];
}

- (IBAction)seUSDBitstamp:(id)sender {
    NSString *str=@"https://www.bitstamp.net/api/ticker/";
    [self.menuExchange setTitle:[NSString stringWithFormat:@"Exchange: Bitstamp(USD)"]];
    NSURL *url=[NSURL URLWithString:str];
    NSData *data=[NSData dataWithContentsOfURL:url];
    NSError *error=nil;
    id response=[NSJSONSerialization JSONObjectWithData:data options:
                 NSJSONReadingMutableContainers error:&error];
    float price = [[response objectForKey:@"last"] floatValue];
    NSString *readable_price = [NSString stringWithFormat:@"$%.2f", price];
    [self updateBitcoinPrice:readable_price];
    [self.updateTimer invalidate];
    self.updateTimer = nil;
    self.updateTimer = [NSTimer scheduledTimerWithTimeInterval:60.0 target:self selector:@selector(seUSDBitstamp:) userInfo:nil repeats:YES];
}

@end