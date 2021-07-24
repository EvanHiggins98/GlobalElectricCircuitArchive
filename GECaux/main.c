/* 
 * File:   main.c
 * Author: asent
 *
 * Created on August 8, 2018, 5:02 PM
 */
// PIC16F689 Configuration Bit Settings
// 'C' source line config statements
// CONFIG
#pragma config FOSC = EXTRCCLK  // Oscillator Selection bits (RC oscillator: CLKOUT function on RA4/OSC2/CLKOUT pin, RC on RA5/OSC1/CLKIN)
#pragma config WDTE = OFF       // Watchdog Timer Enable bit (WDT enabled)
#pragma config PWRTE = OFF      // Power-up Timer Enable bit (PWRT disabled)
#pragma config MCLRE = ON       // MCLR Pin Function Select bit (MCLR pin function is MCLR)
#pragma config CP = OFF         // Code Protection bit (Program memory code protection is disabled)
#pragma config CPD = OFF        // Data Code Protection bit (Data memory code protection is disabled)
#pragma config BOREN = ON       // Brown-out Reset Selection bits (BOR enabled)
#pragma config IESO = ON        // Internal External Switchover bit (Internal External Switchover mode is enabled)
#pragma config FCMEN = ON       // Fail-Safe Clock Monitor Enabled bit (Fail-Safe Clock Monitor is enabled)

///////////////////////////////////////
//FLIGHT CODE AS OF AUGUST 28TH, 2019//
///////////////////////////////////////

#include <xc.h>
#include "pic16f689.h"
#include "Watchdog.h"
#include "UART.h"
#include "GPIO.h"
#include "Timing.h"

#define CUTDOWN_RETRIES 5 //number of times to attempt to send the cutdown message

int main() {
    InitUART();       //initialize UART
    InitGPIO();       //initialize GPIO
    InitWatchdog(); //initialize watchdog
    InitTimer();      //initialize timer
    int retries;      //counter for number of retries attempted
    int cutdown_code; //holds return from cutdown
    SleepXBee();                          //put the XBee to sleep
    while (1) 
    {
        if(ReadString_GPIO("CUT"))            //if "CUT" was received over GPIO
        {
            ExchangeChar_GPIO('?',1);         //send a '?' over GPIO
            retries = 0;                      //set counter to initial value
            cutdown_code = NO_MESSAGE;        //set cutdown code to initial value
            EnableUART();
            while(cutdown_code != SUCCESS  && retries++ < CUTDOWN_RETRIES) //loop until max retries attempted, or a successful cutdown was executed
            {
                cutdown_code = Cutdown();     //attempt to cutdown and store the return code
            }
            DisableUART();
            ResetWatchdog();                //reset the watchdog
            switch(cutdown_code)              //send the status of the cutdown
            {
                case SUCCESS:
                    ExchangeChar_GPIO('K',1); //send a 'K' over GPIO (success)
                    break;

                case UNEXPECTED_MESSAGE:
                    ExchangeChar_GPIO('U',1); //send a 'U' over GPIO (Unexpected response)
                    break;

                case NO_MESSAGE:
                    ExchangeChar_GPIO('N',1); //send an 'N' over GPIO (No response)
                    break;
            }
        }                
        ResetWatchdog();
    }
    return 0;
}
