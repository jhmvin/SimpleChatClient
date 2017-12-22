import netifaces as ni
import _winreg as wr

class MonoNetwork():
    def __init__(self):
       
        pass
    @classmethod
    def translate_iface(self,iface_guids):
        iface_names = iface_guids#['(unknown)' for i in range(len(iface_guids))]
        reg = wr.ConnectRegistry(None, wr.HKEY_LOCAL_MACHINE)
        reg_key = wr.OpenKey(reg, r'SYSTEM\CurrentControlSet\Control\Network\{4d36e972-e325-11ce-bfc1-08002be10318}')
        try:
            reg_subkey = wr.OpenKey(reg_key, iface_guids + r'\Connection')
            iface_names = wr.QueryValueEx(reg_subkey, 'Name')[0]
        except:
            pass
        return iface_names
        pass #end of translate
    
    @classmethod
    def get_ifadress(self,iface_id):
        #gets the card name from registry number {40E3113E-0673-477A-9837-9367A27E8F79} to name
        return ni.ifaddresses(iface_id).get(ni.AF_INET, [])
        pass
    
    pass #end of class

for iface in ni.interfaces():
    card_name = MonoNetwork.translate_iface(iface)
    ip = "Not Connected"
    if(MonoNetwork.get_ifadress(iface) != [] ):
        ip = MonoNetwork.get_ifadress(iface)[0].get('addr')
    
    print "Card Name: ",card_name, " - ", ip



