#ifndef __PID_CONTROLLER_H__
#define __PID_CONTROLLER_H__ 1


class AbstractController {
  public:
    AbstractController () {};
    AbstractController (double setpoint): setpoint(setpoint) {};
    virtual double heaterPower (double dt, double T) = 0;
    void   setSetpoint (double newSetpoint) { setpoint = newSetpoint; };
    double getSetpoint ()                   { return setpoint; };
  
  protected:
    double setpoint = 0;
};


class PidController: public AbstractController {

  public:
    PidController (double setpoint, double Kp, double Ki, double Kd):
        AbstractController(setpoint), Kp(Kp), Ki(Ki), Kd(Kd) {};
    PidController (double setpoint, double Kp) :
        AbstractController(setpoint), Kp(Kp) {};
    PidController () {};

    double heaterPower (double dt, double T);
    
  private:
    double Kp = 0;
    double Ki = 0;
    double Kd = 0;
    double integral = 0;
    double previous_error = 0;
};


#endif 
