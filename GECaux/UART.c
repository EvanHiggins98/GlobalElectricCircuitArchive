#include <xc.h>
#include "pic16f689.h"
#include "GPIO.h"
#include "watchdog.h"
#include "Timing.h"

#define TERMINATE_M_LENGTH 20
#define SUCCESS_M_LENGTH 19

#define UNIT 2
#if UNIT == 1
char TERMINATE_M[] = {0x7E,0x00,0x10,0x17,0x03,0x00,0x13,0xA2,0x00,0x41,0xA2,0x2D,0xDC,0xFF,0xFE,0x02,0x44,0x31,0x05,0xCB};
char SUCCESS_M[] =   {0x7E,0x00,0x0F,0x97,0x03,0x00,0x13,0xA2,0x00,0x41,0xA2,0x2D,0xDC,0xFF,0xFE,0x44,0x31,0x00,0x52};
#endif

#if UNIT == 2
char TERMINATE_M[] = {0x7E,0x00,0x10,0x17,0x03,0x00,0x13,0xA2,0x00,0x41,0xA2,0x2D,0x9E,0xFF,0xFE,0x02,0x44,0x31,0x05,0x09};
char SUCCESS_M[] =   {0x7E,0x00,0x0F,0x97,0x03,0x00,0x13,0xA2,0x00,0x41,0xA2,0x2D,0x9E,0xFF,0xFE,0x44,0x31,0x00,0x90};
#endif

#if UNIT == 3
char TERMINATE_M[] = {0x7E,0x00,0x10,0x17,0x03,0x00,0x13,0xA2,0x00,0x41,0xA2,0x2D,0xA3,0xFF,0xFE,0x02,0x44,0x31,0x05,0x04};
char SUCCESS_M[] =   {0x7E,0x00,0x0F,0x97,0x03,0x00,0x13,0xA2,0x00,0x41,0xA2,0x2D,0xA3,0xFF,0xFE,0x44,0x31,0x00,0x8B};
#endif

#if UNIT == 4
char TERMINATE_M[] = {0x7E,0x00,0x10,0x17,0x03,0x00,0x13,0xA2,0x00,0x41,0xA2,0x2D,0x76,0xFF,0xFE,0x02,0x44,0x31,0x05,0x31};
char SUCCESS_M[] =   {0x7E,0x00,0x0F,0x97,0x03,0x00,0x13,0xA2,0x00,0x41,0xA2,0x2D,0x76,0xFF,0xFE,0x44,0x31,0x00,0xB8};
#endif

enum CUTDOWN_CODE{SUCCESS, UNEXPECTED_MESSAGE, NO_MESSAGE};

void InitUART() {
    
    SPBRGH = 0; //set baud rate to 9600
    SPBRG = 25;
    BRG16 = 0;
    BRGH = 1;
    TXSTAbits.SYNC = 0;
    //TXSTAbits.TXEN=1;   //enable UART for transmitting and receiving in asynchronous mode
    //RCSTAbits.CREN = 1;
    //RCSTAbits.SPEN=1;
}

void EnableUART()
{
    TXSTAbits.TXEN=1;   //enable UART for transmitting and receiving in asynchronous mode
    RCSTAbits.CREN = 1;
    RCSTAbits.SPEN=1;
}

void DisableUART()
{
    TXSTAbits.TXEN = 0;   //enable UART for transmitting and receiving in asynchronous mode
    RCSTAbits.CREN = 0;
    RCSTAbits.SPEN = 0;
}

void SendChar_UART(char c) {
    TXREG=c;                 //place the character into the transmitting FIFO
    while (!TXSTAbits.TRMT); //wait until TXREG is empty
}

void SendString_UART(char *s, int length)
{
    int i;
    for (i = 0;i < length; i++) //loop through each character of the string
        SendChar_UART(*(s++));  //send the current character
}

char ReadChar_UART()
{
    while(!DataInFIFO()); //wait for data to be present in the receiving FIFO
    return RCREG;         //return the top character in the receiving FIFO
}

int DataInFIFO()
{
    return PIR1bits.RCIF; //return FIFO status flag
}

int ParseMessage(char* message)
{
    int index = 0;    //counter for message index
    while(index < SUCCESS_M_LENGTH) //loop until entire message is compared
    {
        if(message[index] != SUCCESS_M[index]) //check to see if current character of message is expected
            return UNEXPECTED_MESSAGE;         //if not, return unexpected message error
        ++index;                               //move to the next character
    }
    return SUCCESS;   //if entire message was compared successfully, return success code
}

void UpdateMessage(char* message, char newChar)
{
    int i;
    for(i = 0; i < SUCCESS_M_LENGTH - 1; ++i)
        message[i] = message[i+1];
    message[SUCCESS_M_LENGTH - 1] = newChar;
}

int Cutdown()
{
    int period = 0;                      //counter for number of timer periods passed
    char message[SUCCESS_M_LENGTH];      //holds message received from XBeeR
    WakeXBee();                          //wake the XBee up
    SendString_UART(TERMINATE_M, TERMINATE_M_LENGTH); //send the terminate message over UART
    StartTimer();                        //start timer
    while(period < TICKS_25SECONDS)                   //loop for 47 timer periods, 25 seconds (47 * 0.524 ~= 25)
    {
        if(RCSTAbits.OERR)
        {
            DisableUART();
            WaitS(1);
            EnableUART();
        }
        while(DataInFIFO())              //if data was received over UART
        {
            UpdateMessage(message, ReadChar_UART());
            if(ParseMessage(message) == SUCCESS)
            {
                SleepXBee();
                return SUCCESS;
            }
        }
        if(PeriodPassed())               //if a timer period has passed
        {
            StartTimer();                //restart the timer
            ++period;                    //update period counter
        }
    }
    SleepXBee();                         //put the XBee to sleep
    return NO_MESSAGE;                   //return error code for no message
}
