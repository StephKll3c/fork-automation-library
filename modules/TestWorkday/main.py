from workday import WorkdayModule
from workday.workday_activity_logging_connector import WorkdayActivityLoggingConnector

if __name__ == "__main__":
    print("Starting Workday module...")
    module = WorkdayModule()
    module.register(WorkdayActivityLoggingConnector, "workday_activity_logging")
    module.run()
