from flask import Flask, render_template
import threading
import pjsua as pj

app = Flask(__name__)

# Configure SIP
sip_account = None

class MyAccountCallback(pj.AccountCallback):
    def __init__(self, account):
        pj.AccountCallback.__init__(self, account)

    def on_incoming_call(self, call):
        global current_call
        current_call = call
        call_cb = MyCallCallback(call)
        call.set_callback(call_cb)
        call.answer(180)

class MyCallCallback(pj.CallCallback):
    def __init__(self, call):
        pj.CallCallback.__init__(self, call)

    def on_state(self):
        print("Call with", self.call.info().remote_uri)
        print("Call state is", self.call.info().state_text, self.call.info().last_code, self.call.info().last_reason)

    def on_media_state(self):
        if self.call.info().media_state == pj.MediaState.ACTIVE:
            call_slot = self.call.info().conf_slot
            pj.Lib.instance().conf_connect(call_slot, 0)
            pj.Lib.instance().conf_connect(0, call_slot)
            print("Media is active")

def sip_thread():
    global sip_account
    lib = pj.Lib()
    lib.init(log_cfg=pj.LogConfig(level=3, callback=None))
    transport = lib.create_transport(pj.TransportType.UDP, pj.TransportConfig(5060))
    lib.start()
    acc_cfg = pj.AccountConfig("185.74.7.73", "787777711", "blablabla123A")
    sip_account = lib.create_account(acc_cfg, cb=MyAccountCallback)

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    threading.Thread(target=sip_thread).start()
    app.run(host='0.0.0.0', port=5000)
