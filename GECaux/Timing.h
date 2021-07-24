/* 
 * File:   Timing.h
 * Author: Collin MacDicken
 *
 * Created on January 8, 2019, 7:58 PM
 */

#ifndef TIMING_H
#define	TIMING_H

#define TICKS_25SECONDS 47

//initialize timer
void InitTimer();

//wait for s seconds
void WaitS(int s);

//starts the timer
void StartTimer();

//checks to see if a timer period has passed, stops timer and clears overflow flag if so
int PeriodPassed();

#endif	/* TIMING_H */
