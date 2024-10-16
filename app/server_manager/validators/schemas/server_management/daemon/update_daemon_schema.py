from marshmallow import Schema, fields, validate, ValidationError


class UpdateDaemonSchema(Schema):
    command = fields.Str(required=True)
    directory = fields.Str(missing='/')
    user = fields.Str(missing='root')
    daemon_id = fields.Str(required=True)
    num_processes = fields.Int(required=True, missing=1)
    start_seconds = fields.Int(required=True, missing=1)
    stop_seconds = fields.Int(required=True, missing=5)
    stop_signal = fields.Str(required=True, validate=validate.OneOf(['SIGHUP', 'SIGINT', 'SIGQUIT', 'SIGILL', 'SIGTRAP', 'SIGABRT', 'SIGIOT', 'SIGBUS', 'SIGEMT', 'SIGFPE', 'SIGKILL', 'SIGUSR1', 'SIGSEGV', 'SIGUSR2', 'SIGTERM', 'SIGSTKFLT', 'SIGCHLD', 'SIGCLD', 'SIGCONT', 'SIGSTOP', 'SIGTSTP', 'SIGTTIN', 'SIGTTOU', 'SIGURG', 'SIGXCPU', 'SIGXFSZ', 'SIGVTALRM', 'SIGPROF', 'SIGWINCH', 'SIGIO', 'SIGPOLL', 'SIGPWR', 'SIGINFO', 'SIGLOST', 'SIGSYS', 'SIGPIPE', 'SIGALRM']))