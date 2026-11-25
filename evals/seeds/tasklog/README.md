# tasklog

Tiny command-line time log. Entries are stored in a JSON file (default `tasklog.json`, override with `TASKLOG_FILE`).

    tasklog add <project> <minutes> [note...]   record an entry
    tasklog list                                 show all entries
    tasklog report                               minutes per project, with a total

Run the tests with `npm test`.
