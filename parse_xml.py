import xml.etree.ElementTree as ET
import sys

xml_path = sys.argv[1] if len(sys.argv) > 1 else 'Galileo_G87173_204.xml'

def parse_xml(path):
    tree = ET.parse(path)
    root = tree.getroot()
    stackup = root.find('Stackup')
    materials = stackup.find('Materials').findall('Material')
    layers = stackup.find('Layers').findall('Layer')
    print(f'Parsed {len(materials)} materials and {len(layers)} layers')
    for i, layer in enumerate(layers[:5]):  # show first 5 layers
        print(f'Layer {i+1}: name={layer.get("Name")} type={layer.get("Type")}')

if __name__ == '__main__':
    parse_xml(xml_path)
