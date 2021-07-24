#include <xc.h>
#include "pic16f689.h"
#include "Timing.h"

#define OUT_DATA1 PORTCbits.RC7
#define OUT_DATA0 PORTCbits.RC6
#define OUT_TxEnable PORTCbits.RC3
#define IN_CLK0 PORTCbits.RC4
#define IN_CLK1 PORTCbits.RC5
#define IN_TxEnable PORTCbits.RC2
#define IN_DATA1 PORTCbits.RC1
#define IN_DATA0 PORTCbits.RC0

#define XBEE_SLEEP PORTBbits.RB6
#define PIC_SLEEP PORTAbits.RA2

void InitGPIO()
{
    INTCONbits.RABIE = 1; //enable interrupts on registers A and B
    IOCAbits.IOCA2 = 1;   //enable interrupt-on-change on RA2
    INTCONbits.RABIF = 0; //clear the interrupt-on-change flag
    TRISAbits.TRISA2 = 1; //set RA2 to input
    TRISBbits.TRISB6 = 0;
    TRISC = 0b00110111;   //set each PortC pin to their corresponding directions
    ANSEL=0;              //disable analog functions on all pins
    ANSELH=0;
    OUT_TxEnable = 0;     //set transmitting flag to 0
    OUT_DATA0 = 0;        //set transmitting data to 0
    OUT_DATA1 = 0;
    XBEE_SLEEP = 1;       //put the XBee to sleep
}

char ExchangeChar_GPIO(char c, char transmit)
{
    unsigned int qByte = 0;     //initialize quarter-byte counter
    char result = 0;            //data received from PIC32
    
    if(transmit)
      OUT_TxEnable = 1;         //set transmit enable signal
    else
      OUT_TxEnable = 0;
    
    while(!IN_TxEnable){}
    while(IN_CLK0 || IN_CLK1){}   //wait for the 0th quarter-byte on the clock
    
    do                                                               //loop for all four quarter-bytes
    {   
        OUT_DATA0 = (c & (1 << (qByte * 2))) >> (qByte * 2);         //set 0th bit of current quarter-byte
        OUT_DATA1 = (c & (1 << (1 + qByte * 2))) >> (1 + qByte * 2); //set 1st bit of current quarter-byte
        if(IN_TxEnable)                                              //if the PIC32 is sending information
        {
            //store the received information into the proper quarter-byte of result
            result += (IN_DATA0 << (qByte * 2)) + (IN_DATA1 << (1 + qByte * 2));
        }
        unsigned int cCLK = IN_CLK0;                                 //store the current value of clock bit 0
        while(cCLK == IN_CLK0){}                                     //wait until clock bit 0 changes

        qByte = IN_CLK0 + IN_CLK1 * 2;                               //update the quarter byte counter
    }
    while(qByte != 0);
    
    OUT_TxEnable = 0;
    return result;                                                   //return the data received by the PIC32
}

void SendString_GPIO(char *s)
{
    for (;*s;s++)                  //loop up to the last character of the string
        ExchangeChar_GPIO(*s, 1);  //send the current character
}

int ReadString_GPIO(char *s)
{
    for(;*s;s++)                         //loop through the string
    {
        if(*s != ExchangeChar_GPIO(0,0)) //if the next read character is the same as the next character in the string
            return 0;                    //return a false condition
    }
    return 1;                            //return a true condition
}

void WakeXBee()
{
    XBEE_SLEEP = 0; //output a low signal on sleep pin to wake the XBee
    WaitS(1);       //wait for 1 second to give the Xbee time to wake up
}

void SleepXBee()
{
    XBEE_SLEEP = 1; //output a high signal on sleep pin to sleep XBee
}

void SleepPic()
{
    PIC_SLEEP;            //store current state of sleep pin
    __asm("SLEEP");       //go to sleep
                          //WAKE
    INTCONbits.RABIF = 0; //clear interrupt flag
    PIC_SLEEP;            //store new state of sleep pin
}
