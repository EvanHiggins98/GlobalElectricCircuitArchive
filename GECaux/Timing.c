#include <xc.h>
#include "pic16f689.h"
#include "Watchdog.h"

void InitTimer()
{
    T1CONbits.TMR1GE = 0;  //set timer to always count
    T1CONbits.T1CKPS0 = 1; //1:8 prescaler value
    T1CONbits.T1CKPS1 = 1;
    T1CONbits.T1OSCEN = 0; //disable LP oscillator
    T1CONbits.TMR1CS = 0;  //Internal clock (Fosc/4)
    PIR1bits.TMR1IF = 0;   //clear timer interrupt flag
}

void WaitS(int s)
{
    int i, j;                         //looping variables
    for(i = 0; i < s; i++)            //loop for number of seconds
    {
        //ResetWatchdog();              //reset the watchdog
        TMR1H = 0;                    //set timer counters to 0
        TMR1L = 0;
        PIR1bits.TMR1IF = 0;          //clear the timer overflow flag
        T1CONbits.TMR1ON = 1;         //start the timer
        for(j = 0; j < 2; j++)        //loop 2 times (timer period ~= 1/2 seconds)
        {
            while(!PIR1bits.TMR1IF){} //wait for the counter registers to overflow
            PIR1bits.TMR1IF = 0;      //clear the timer overflow flag
        }
        T1CONbits.TMR1ON = 0;         //stop the timer
    }
}

void StartTimer()
{
    TMR1H = 0;                    //set counter registers to 0
    TMR1L = 0;
    PIR1bits.TMR1IF = 0;          //clear timer overflow flag
    T1CONbits.TMR1ON = 1;         //start the timer
}

int PeriodPassed()
{
    if(PIR1bits.TMR1IF)       //if a timer period has passed (1/2 second)
    {
        PIR1bits.TMR1IF = 0;  //clear the timer overflow flag
        T1CONbits.TMR1ON = 0; //stop the timer
        return 1;             
    }
    
    return 0;
}
