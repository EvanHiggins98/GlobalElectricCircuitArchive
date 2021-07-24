/* 
 * File:   UART.h
 * Author: ADMIN
 *
 * Created on August 8, 2018, 6:51 PM
 */

#ifndef UART_H
#define	UART_H

//enumeration of cutdown status codes
enum CUTDOWN_CODE{SUCCESS, UNEXPECTED_MESSAGE, NO_MESSAGE};

//initialize UART
void InitUART();

//send a specified character over UART
void SendChar_UART(char c);

//enable the UART module
void EnableUART();

//disable the UART module
void DisableUART();

//send a specified string over UART
void SendString_UART(char *s, int length);

//returns the first unread character in the UART receiving FIFO
char ReadChar_UART();

//returns 0 if there is no data in the input FIFO, 1 otherwise
int DataInFIFO();

//attempts a cutdown and returns a cutdown code depending on results
int Cutdown();

#endif	/* UART_H */
