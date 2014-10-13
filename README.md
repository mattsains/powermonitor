powermonitor
============

This is the code for the power monitoring project.

If you're interested in the microcontroller's code, check out the example code in ./Firmware/Examples/

Current list of required python packages:
- apscheduler < 3.0 (Requires sqlalchemy for database jobstore)
- beautifulsoup4
- django == 1.6.5 (This is what we started developing with. Don't want to change it just yet)
- inlinestyler (if not using premailer)
- matplotlib
- numpy
- pandas (Requires: numpy, python-dateutil, pytz)
- patsy
- premailer (If not using inlinestyler)
- pymysql
- python-dateutil
- pytz
- scipy (Requires fortran to install)
- spidev
- sqlalchemy
- statsmodels (Requires patsy, scipy)
