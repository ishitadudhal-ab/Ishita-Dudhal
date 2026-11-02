from app.logic.machine_interface import MachineInterface;
mi = MachineInterface('opc.tcp://127.0.0.1:4840/wms-test/server/');
mi.connect();
print('control=', mi.is_control_enabled(), 'safe=', mi.is_safe()); 
mi.trigger_store(); mi.trigger_retrieve(); 
print('triggers=', mi._get_node('einlagern').get_value(), mi._get_node('auslagern').get_value()); 
mi.disconnect()
