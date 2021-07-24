#include "pic16f689.h"
void InitWatchdog(void)
{
    WDTCONbits.WDTPS3 = 1;      //set Watchdog timer to time out after 72 seconds
    WDTCONbits.WDTPS2 = 0;
    WDTCONbits.WDTPS1 = 0;
    WDTCONbits.WDTPS0 = 1;
    WDTCONbits.SWDTEN = 1;      //enable the watchdog timer
}

void ResetWatchdog(void)
{
    __asm("CLRWDT;"); //clear the watchdog timer
}
