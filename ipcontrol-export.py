import re
import sys
from suds.plugin import MessagePlugin
from suds.transport.http import HttpAuthenticated
from suds.client import Client
from suds.sax.element import Element
from creds import user, pw


class MyPlugin(MessagePlugin):
    def __init__(self):
        self.last_sent_raw = None
        self.last_received_raw = None

    def sending(self, context):
        self.last_sent_raw = str(context.envelope)

    def received(self, context):
        self.last_received_raw = str(context.reply)


def main():

    # Build transport and client objects using HttpAuth for authentication
    # and MessagePlugin to allow the capturing of raw XML, necessary for
    # extracting the IPControl session ID later

    plugin = MyPlugin()
    credentials = dict(username=user, password=pw)
    transport = HttpAuthenticated(**credentials)
    client = Client(
        'http://ipcontrol.foobar.net/inc-ws/services/Exports?wsdl',
        headers={'username':user, 'password':pw},
        transport=transport,
        plugins=[plugin]
        )

    query_parameters = ('ipaddress = 1.2.3.4', False)  # The boolean is for includeFreeBlocks

    # Exports must be initialized first. The IPControl session ID can then
    # be extracted from the raw reply data. This is necessary later when
    # the export service is called.

    context = client.service.initExportChildBlock(*query_parameters)
    session_id_re = re.search(r'([0-9-]{19,20})', str(plugin.last_received_raw), re.M)
    if session_id_re:
        session_id = session_id_re.group(1)
        print("SESSION ID: {}".format(session_id))
    else:
        print("NO SESSION ID FOUND")
        sys.exit()

    # Build a new SOAP header where the 'sessionID' is set to the value extracted
    # from the raw initialization reply data above, then apply the new
    # header to the existing client object.

    sid = Element('sessionID', ns=('ns1', 'http://xml.apache.org/axis/session')).setText(session_id)
    sid.set("SOAP-ENV:mustUnderstand", "0")
    sid.set("SOAP-ENV:actor", "http://schemas.xmlsoap.org/soap/actor/next")
    sid.set("xsi:type", "soapenc:long")
    client.set_options(soapheaders=sid)

    result = client.service.exportChildBlock(context)
    print("RESULT: {}".format(result))

if __name__ == '__main__':
    main()
