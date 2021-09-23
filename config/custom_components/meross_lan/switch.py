from homeassistant.components.switch import SwitchEntity, DEVICE_CLASS_OUTLET
from homeassistant.const import STATE_OFF, STATE_ON

from .merossclient import const as mc  # mEROSS cONST
from .meross_entity import _MerossToggle, platform_setup_entry, platform_unload_entry
from .const import DND_ID, PLATFORM_SWITCH


async def async_setup_entry(hass: object, config_entry: object, async_add_devices):
    platform_setup_entry(hass, config_entry, async_add_devices, PLATFORM_SWITCH)

async def async_unload_entry(hass: object, config_entry: object) -> bool:
    return platform_unload_entry(hass, config_entry, PLATFORM_SWITCH)



class MerossLanSwitch(_MerossToggle, SwitchEntity):
    """
    generic plugs (single/multi outlet and so)
    """
    PLATFORM = PLATFORM_SWITCH


    def __init__(self, device: 'MerossDevice', id: object, toggle_ns: str, toggle_key: str):
        super().__init__(device, id, DEVICE_CLASS_OUTLET, toggle_ns, toggle_key)


class MerossLanDND(_MerossToggle, SwitchEntity):
    """
    Do Not Disturb mode for devices supporting it (i.e. comfort lights on switches)
    """
    PLATFORM = PLATFORM_SWITCH


    def __init__(self, device: 'MerossDevice'):
        super().__init__(device, DND_ID, mc.KEY_DNDMODE, None, None)


    @property
    def entity_registry_enabled_default(self) -> bool:
        return False


    """
    async def async_added_to_hass(self) -> None:
        # this device is likely to be disabled in HA so we just
        # add polling when enabled
        self._device.polling_dictionary[mc.NS_APPLIANCE_SYSTEM_DND] = {}
    async def async_will_remove_from_hass(self) -> None:
        self._device.polling_dictionary.pop(mc.NS_APPLIANCE_SYSTEM_DND, None)
    """

    async def async_turn_on(self, **kwargs) -> None:

        def _ack_callback():
            self._set_state(STATE_ON)

        # WARNING: on MQTT we'll loose the ack callback since
        # it's not (yet) implemented and the option to correctly
        # update the state will be loosed since the ack payload is empty
        # right now 'force' http proto even tho that could be disabled in config
        await self._device.async_http_request(
            mc.NS_APPLIANCE_SYSTEM_DND,
            mc.METHOD_SET,
            {mc.KEY_DNDMODE: {mc.KEY_MODE: 1}},
            _ack_callback
        )


    async def async_turn_off(self, **kwargs) -> None:

        def _ack_callback():
            self._set_state(STATE_OFF)

        await self._device.async_http_request(
            mc.NS_APPLIANCE_SYSTEM_DND,
            mc.METHOD_SET,
            {mc.KEY_DNDMODE: {mc.KEY_MODE: 0}},
            _ack_callback
        )