/* 
 * File:   GPIO.h
 * Author: ADMIN
 *
 * Created on August 8, 2018, 7:26 PM
 */
/*
      PIC16  <->  PIC32         - FUNCTION

pin9  | RC7   -> pin5   | RE7   - PIC16_DATA1
pin8  | RC6   -> pin4   | RE6   - PIC16_DATA0
pin7  | RC3   -> pin99  | RE3   - PIC16_TxEnable
pin6  | RC4  <-  pin100 | RE4   - PIC32_CLK0
pin5  | RC5  <-  pin3   | RE5   - PIC32_CLK1
pin14 | RC2  <-  pin98  | RE2   - PIC32_TxEnable
pin15 | RC1  <-  pin94  | RE1   - PIC32_DATA1
pin16 | RC0  <-  pin93  | RE0   - PIC32_DATA0

            CLOCK (NOT CURRENTLY USED)
pin17 | RA2  <->  pin18  | RE8
*/

#ifndef GPIO_H
#define	GPIO_H

//initialize GPIO
void InitGPIO();

//send a character over GPIO to the PIC32, returns the received character from the PIC32
char ExchangeChar_GPIO(char c, char transmit);

//sends a string of characters over GPIO to the PIC 32
void SendString_GPIO(char *s);

//returns 1 is the passed string matches what is being read from the PIC32, 0 if not
int ReadString_GPIO(char *s);

//wakes the XBee up
void WakeXBee();

//puts the Xbee to sleep
void SleepXBee();

//puts the PIC to sleep, will wake up when state of RA2 is changed
void SleepPic();

#endif	/* GPIO_H */
