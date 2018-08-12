import json

from tools import Tools

home_path = "/home/houfa"
#home_path = "D:\\Code\\ThingTrust"
source_path = "{0}/mainchain".format(home_path)
testnet_builder_path = "{0}/testnet-builder".format(source_path)
testnet_builder_data_path = "{0}/data".format(testnet_builder_path)
trustnote_headless_path = "{0}/trustnote-headless".format(testnet_builder_path)
trustnote_headless_play_path = "{0}/play".format(trustnote_headless_path)
trustnote_hub_path = "{0}/trustnote-hub".format(testnet_builder_path)
trustnote_witness_path = "{0}/trustnote-witness".format(testnet_builder_path)
trustnote_explorer_path = "{0}/trustnote-explorer".format(testnet_builder_path)

configs_files_path = "{0}/config-files".format(testnet_builder_path)
config_path = "{0}/.config".format(home_path)
shell_path = "{0}/shell".format(source_path)

old_first_utxo = "IO3JFSLJQVS4GNWR6I4QYIPBYGIUF3ZF"
old_from_address = "IO3JFSLJQVS4GNWR6I4QYIPBYGIUF3ZF"
old_payee_address= "XIM76DRNUNFWPXPI5AGOCYNMA3IOXL7V"
old_gensis_unit = "Ffrmbl8JSMhkflvwiH7Cfo8xs/oX1bRcda38IVUhtEo="
web_port = 8080

gensis_filter_anchor = ">>->> Genesis d, hash="

class MainChainSetter:
    """Setup main chain run environment."""
    first_utxo = ""
    from_address = ""
    payee_address = ""
    gensis_unit = ""
    peers = ["127.0.0.1:6616", "127.0.0.1:6617"]
    protocol = "ws"
    all_addresses = []
    headless_addresses = []
    witness_addresses = []

    def __init__(self):
        return

    def setup_os_env(self):
        Tools.run_shell_command("sudo {0}/setup_os_env.sh".format(shell_path))
        return

    def load_code(self):
        Tools.run_shell_command("{0}/loadcode.sh".format(shell_path))
        return

    def create_genesis(self):
        self.setup_create_genesis()

        Tools.log("----Please press [enter] after 5s.----")
        Tools.run_shell_command("rm -f {0}/headless15/trustnote*".format(config_path))
        Tools.run_shell_cd(trustnote_headless_play_path)
        output = Tools.run_shell_command_with_output("node create_genesis.js")
        Tools.run_shell_cd(home_path)
        Tools.log(output)

        self.gensis_unit = self.read_genesis_unit(output)
        Tools.log("Gensis unit is {0}".format(self.gensis_unit))
        self.update_genesis()
        self.update_witnesses()

        Tools.run_shell_command("cp {0}/hub-conf.js {1}/conf.js".format(configs_files_path, trustnote_hub_path))
        Tools.run_shell_command("cp {0}/constants.js {1}/node_modules/trustnote-common/constants.js".format(configs_files_path, trustnote_hub_path))

        return

    def setup_hub(self, index, protocol, port):
        current_project_path = "{0}{1}".format(trustnote_hub_path, index)

        self.copy_project(trustnote_hub_path, current_project_path)
        self.update_package_name("trustnote-hub", "hub{0}".format(index), current_project_path)

        #update protocol
        protocol_modify_dictionary = { 
            "wss://" : "{0}://".format(protocol),
            "6655" : "{0}".format(port),
            "exports.port = 6616" : "exports.port = {0}".format(port)
        }
        Tools.file_lines_replacer("{0}/conf.js".format(current_project_path), protocol_modify_dictionary)
        Tools.file_lines_replacer("{0}/node_modules/trustnote-common/conf.js".format(current_project_path), protocol_modify_dictionary)

        #update peers
        peers_modify_dictionary = { 
            "\'wss://victor.trustnote.org/tn\'," : "\'{0}\',".format(self.peers[0]),
            "\'wss://eason.trustnote.org/tn\'," : "\'{0}\',".format(self.peers[1]),
            "\'wss://lymn.trustnote.org/tn\'," : "",
            "\'wss://bob.trustnote.org/tn\'," : "",
            "\'wss://curry.trustnote.org/tn\'," : "",
            "\'wss://kake.trustnote.org/tn\'" : ""
        }
        Tools.file_lines_replacer("{0}/conf.js".format(current_project_path), peers_modify_dictionary)

        Tools.run_shell_command("pm2 start {0}/start.js --name hub{1}".format(current_project_path, index))

        return

    def setup_hubs(self):
        self.setup_hub(1, self.protocol, 6616)
        self.setup_hub(2, self.protocol, 6617)
        return

    def setup_witness(self, index, hub_url):
        current_project_path = "{0}{1}".format(trustnote_witness_path, index)

        self.copy_project(trustnote_witness_path, current_project_path)
        self.update_package_name("trustnote-witness", "witness{0}".format(index), current_project_path)
        
        #copy files from configs files
        Tools.run_shell_command("cp -R {0}/witness{1} {2}/".format(testnet_builder_data_path, index, config_path))
        Tools.run_shell_command("cp {0}/witness-conf.js {1}/conf.js".format(configs_files_path, current_project_path))
        Tools.run_shell_command("cp {0}/witness-start.js {1}/start.js".format(configs_files_path, current_project_path))
        Tools.run_shell_command("cp {0}/witness-headless-start.js {1}/node_modules/trustnote-headless/start.js".format(configs_files_path, current_project_path))
        Tools.run_shell_command("cp {0}/constants.js {1}/node_modules/trustnote-common/constants.js".format(configs_files_path, current_project_path))

        #update conf.js
        conf_modify_dictionary = { 
            "newton.trustnote.org/tn" : hub_url,
            "wss://" : "{0}://".format(self.protocol)
        }
        Tools.file_lines_replacer("{0}/conf.js".format(current_project_path), conf_modify_dictionary)
        Tools.file_lines_replacer("{0}/node_modules/trustnote-common/conf.js".format(current_project_path), conf_modify_dictionary)

        Tools.run_shell_command("pm2 start {0}/start.js --name witness{1}".format(trustnote_witness_path, index))

        return

    def setup_witnesses(self):
        for i in range(1, 7):
            self.setup_witness(i, self.peers[0])
        
        for i in range(7, 13):
            self.setup_witness(i, self.peers[1])
        return

    def setup_explorer(self, index, hub_url):
        current_project_path = "{0}{1}".format(trustnote_explorer_path, index)

        self.copy_project(trustnote_explorer_path, current_project_path)
        self.update_package_name("trustnote-explorer", "explorer{0}".format(index), current_project_path)

        Tools.run_shell_command("cd {0}/explorer-conf.js {1}/conf.js".format(configs_files_path, current_project_path))
        Tools.run_shell_command("cd {0}/constants.js {1}/node_modules/trustnote-common/constants.js".format(configs_files_path, current_project_path))

        initial_peers_modify_dictionary = { "exports.webPort = 6000" : "exports.webPort = {0}".format(web_port) }
        Tools.file_lines_replacer("{0}/conf.js".format(current_project_path), initial_peers_modify_dictionary)

        #update peers
        peers_modify_dictionary = { 
            "\'wss://victor.trustnote.org/tn\'," : "\'{0}\',".format(self.peers[0]),
            "\'wss://eason.trustnote.org/tn\'," : "\'{0}\'".format(self.peers[1]),
            "\'wss://lymn.trustnote.org/tn\'," : "",
            "\'wss://bob.trustnote.org/tn\'," : "",
            "\'wss://curry.trustnote.org/tn\'," : "",
            "\'wss://kake.trustnote.org/tn\'" : ""
        }
        Tools.file_lines_replacer("{0}/conf.js".format(current_project_path), peers_modify_dictionary)

        Tools.run_shell_command("pm2 start {0}/explorer.js --name explorer{1}".format(current_project_path, index))

        return

    def setup_exploreres(self):
        self.setup_explorer(1, self.peers[0])
        return

    def setup_headless(self, index):
        current_project_path = "{0}{1}".format(trustnote_headless_path, index)

        self.copy_project(trustnote_headless_path, current_project_path)
        self.update_package_name("trustnote-headless", "headless{0}".format(index), current_project_path)

        #update conf.js
        conf_modify_dictionary = { 
            "exports.hub = \'curry.trustnote.org/tn\'" : "exports.hub = \'{0}\'".format(self.peers[0]),
            "exports.WS_PROTOCOL = \"wss://\"" : "exports.WS_PROTOCOL = \"{0}://\"".format(self.protocol)
        }
        Tools.file_lines_replacer("{0}/conf.js".format(current_project_path), conf_modify_dictionary)
        Tools.file_lines_replacer("{0}/node_modules/trustnote-common/conf.js".format(current_project_path), conf_modify_dictionary)
        
        #copy created headless data to .config
        Tools.run_shell_command("cp {0}/headless{1}/* {2}/".format(testnet_builder_data_path, index, config_path))

        Tools.run_shell_command("pm2 start {0}/start.js --name headless{1}".format(current_project_path, index))

        return

    def setup_headlesses(self):
        for index in range(13, 16):
            self.setup_headless(index)
        return

    def generate_configs(self):
        Tools.run_shell_command("sudo {0}/generateconfigs.sh".format(shell_path))
        self.read_addresses()
        return

    def read_addresses(self):
        all_addresses_path = "{0}/allAddress.json".format(testnet_builder_data_path)
        witnesses_addresses_path = "{0}/witnessAddress.json".format(testnet_builder_data_path)

        self.all_addresses = Tools.read_file_to_json(all_addresses_path)
        self.witness_addresses = Tools.read_file_to_json(witnesses_addresses_path)
        self.headless_addresses = list(set(self.all_addresses).difference(set(self.witness_addresses)))

        self.first_utxo = self.headless_addresses[0]
        self.from_address = self.headless_addresses[1]
        self.payee_address = self.headless_addresses[2]

        return

    def setup_create_genesis(self):
        self.generate_configs()

        modify_dictionary = {
        "require(\'trustnote-headless\')" : "require(\'../start\')", 
        "require(\"trustnote-headless\")" : "require(\"../start\")", 
        old_first_utxo : self.first_utxo,
        old_from_address : self.from_address,
        old_payee_address : self.payee_address
        }

        path = "{0}/create_genesis.js".format(trustnote_headless_play_path)
        Tools.file_lines_replacer(path, modify_dictionary)
        
        return

    def read_genesis_unit(self, content):
        start = content.index(gensis_filter_anchor) + len(gensis_filter_anchor)
        return content[start : start + 44]

    def update_genesis(self):
        modify_dictionary = { old_gensis_unit : self.gensis_unit }
        Tools.file_lines_replacer("{0}/constants.js".format(configs_files_path), modify_dictionary)
        return
    
    def update_witnesses(self):
        modify_dictionary = { 
            "5SGHGVDCY4BO5DKNC5L2TOCAKFNATB5V" : self.witness_addresses[0],
            "5Y7QZSQNKYS5SJVXE47YGQ35FG5JJMXN" : self.witness_addresses[1],
            "AWIA2BFATICIWVVHVCU2N4WZXHP4CD7G" : self.witness_addresses[2],
            "BKRWK7HADRMDZF7IU3B7AYT4WXUWBFGT" : self.witness_addresses[3],
            "CLAGUVFRUSMDWLTIKD5X3BCEXYLG5FKH" : self.witness_addresses[4],
            "LWOUHPD6W27QIMB3S6MYHS7YOVCYFJAF" : self.witness_addresses[5],
            "N4ZBL7XC2TSWC6U6SB4E5V3PFR75MVSU" : self.witness_addresses[6],
            "NRLOKJI2QGVE4CFILL4AIDWXOIMNYQA7" : self.witness_addresses[7],
            "NT5WOZCCWYYKMXGAXKXEVJDYVXMHKHMX" : self.witness_addresses[8],
            "R62HF6RQFPC2NLZ5AWJUWSEQOWYDJGJV" : self.witness_addresses[9],
            "TCO4S66J6WL4JHGVDPTCDLXF6FHXVV5B" : self.witness_addresses[10],
            "WJ66AZLXSTPOZNHFBP4HCZYJ6HHY3FNI" : self.witness_addresses[11]
        }

        Tools.file_lines_replacer("{0}/hub-conf.js".format(configs_files_path), modify_dictionary)
        Tools.file_lines_replacer("{0}/explorer-conf.js".format(configs_files_path), modify_dictionary)
        return

    def copy_project(self, project_full_name, project_short_name):
        Tools.run_shell_command("cp -R {0} {1}".format(project_full_name, project_short_name))
        return

    def update_package_name(self, project_full_name, project_short_name, project_path):
        name_modify_dictionary = { "\"name\": \"{0}\"".format(project_full_name) : "\"name\": \"{1}\"".format(project_full_name, project_short_name) }
        Tools.file_lines_replacer("{0}/package.json".format(project_path), name_modify_dictionary)
        return

    def read_headless_address(self):
        return

try:
    main_chain_setter = MainChainSetter()
    #main_chain_setter.setup_os_env()
    #main_chain_setter.load_code()
    main_chain_setter.create_genesis()
    main_chain_setter.setup_hubs()
    main_chain_setter.setup_witnesses()
    main_chain_setter.setup_exploreres()
    main_chain_setter.setup_headlesses()
    
except Exception as error:
    Tools.log(error)
    
