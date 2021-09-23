from .merossclient import KeyType, const as mc  # mEROSS cONST
from .meross_device import MerossDevice
from .light import MerossLanLight
from .helpers import LOGGER

class MerossDeviceBulb(MerossDevice):

    def __init__(self, api, descriptor, entry) -> None:
        super().__init__(api, descriptor, entry)

        try:
            # we expect a well structured digest here since
            # we're sure 'light' key is there by __init__ device factory
            p_digest = self.descriptor.digest
            p_light = p_digest[mc.KEY_LIGHT]
            if isinstance(p_light, list):
                for l in p_light:
                    MerossLanLight(self, l.get(mc.KEY_CHANNEL, 0), p_digest.get(mc.KEY_TOGGLEX))
            elif isinstance(p_light, dict):
                MerossLanLight(self, p_light.get(mc.KEY_CHANNEL, 0), p_digest.get(mc.KEY_TOGGLEX))

        except Exception as e:
            LOGGER.warning("MerossDeviceBulb(%s) init exception:(%s)", self.device_id, str(e))


    def receive(
        self,
        namespace: str,
        method: str,
        payload: dict,
        header: dict
    ) -> bool:

        if super().receive(namespace, method, payload, header):
            return True

        if namespace == mc.NS_APPLIANCE_CONTROL_LIGHT:
            self._parse_light(payload.get(mc.KEY_LIGHT))
            return True

        return False


    def _parse_light(self, payload) -> None:
        if isinstance(payload, dict):
            self.entities[payload.get(mc.KEY_CHANNEL)]._set_light(payload)
