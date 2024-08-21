# TrackLogging

TrackLogging is a logging package for tracing function calls with error handling and email notification.

## Installation

You can install TrackingLog using pip:

```bash
pip install trackinglog

```

## version History

0.1.0 Package Draft created

0.1.1 Decorator get_log and directly object creator get_logger created. Added setup check decorator. Added p-functions(print and log).

0.1.2 Added error handling. Added verbose option for decorator. Added called function name.

0.1.3 Added profiler for both function level and line level. Updated error handling logic: reset verbose to False, but it will now raise error instead. Added class name to log. Added dependency pakages.
## Feature in developing

Add error handling

Add print to log functions

Add public and private log

Add email notification

Add performance tracking

Add Kafka message notification

Add cache log cleaner