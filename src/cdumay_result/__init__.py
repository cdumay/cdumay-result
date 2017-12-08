#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
.. codeauthor:: Cédric Dumay <cedric.dumay@gmail.com>


"""
from uuid import uuid4
from cdumay_rest_client.exceptions import HTTPException


def data2list(data):
    """ Format anything as list

    :param Any data: input data
    :rtype: list
    """
    if isinstance(data, (list, tuple)):
        return list(data)
    elif data:
        return [data]
    else:
        return list()


class Result(object):
    def __init__(self, retcode=0, stdout=None, stderr=None, retval=None,
                 uuid=None):
        self.retcode = retcode
        self.stdout = data2list(stdout)
        self.stderr = data2list(stderr)
        self.retval = retval or dict()
        self.uuid = uuid if uuid else uuid4()

    def is_error(self):
        return self.retcode != 0

    def print(self, data):
        """Store text in result's stdout

        :param Any data: Any printable data
        """
        self.stdout.append(data)

    def print_err(self, data):
        """Store text in result's stderr

        :param Any data: Any printable data
        """
        self.stderr.append(data)

    @staticmethod
    def fromError(err, uuid=None):
        """ Serialize error as result

        :param cdumay_error.Error err: Error to serialize
        :param uuid.UUID uuid: Error uuid
        :rtype: :class:`kser.result.Result`
        """
        return Result(
            uuid=err.extra.get("uuid", uuid), retcode=err.code,
            stderr=err.message, retval=err.extra
        )

    @staticmethod
    def fromException(exc, uuid=None):
        """ Serialize an exception into a result

        :param Exception exc: Exception raised
        :param str uuid: Current Kafka :class:`kser.transport.Message` uuid
        :rtype: :class:`kser.result.Result`
        """
        if not isinstance(exc, HTTPException):
            exc = HTTPException(code=500, message=str(exc))

        return Result(
            uuid=exc.extra.get("uuid", uuid or uuid4()),
            retcode=exc.code, stderr=exc.message,
            retval=dict(error=exc)
        )

    def __add__(self, o):
        """Add two results

        :param cdumay_result.Result o: the other result
        :rtype: cdumay_result.Result
        """
        self.retcode = self.retcode if self.retcode > o.retcode else o.retcode
        self.retval.update(o.retval)
        self.stdout += o.stdout
        self.stderr += o.stderr
        return self

    def __str__(self):
        return "\n".join(self.stdout if self.retcode == 0 else self.stderr)

    def __repr__(self):
        return "Result<retcode='{}'>".format(self.retcode)
