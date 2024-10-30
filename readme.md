# Vietnamese Address Parser

Identifies and parses a Vietnamese address string into country, house number, street name, and the 3 respective municipal levels. Can parse addresses that are space-separated, with spelling errors, abbreviated or out-of-order elements. Any elements that can not be parsed will go into the *Unparsed* section

### Example usage:
#### No spelling error, with out-of-order and abbreviated elements:
  ```python
  from AddressParser.Parser import Parser
  from pprint import pprint

  parser = Parser()
  test_address = "47/9B Tô Ký Q.12 Phường Trung Mỹ Tây TPHCM"
  parser.parse_address(test_address)
  ```
  ```python
  {'Country': '',
  'House Number': '47/9B',
  'Municipal Level 1': 'THANH PHO HO CHI MINH',
  'Municipal Level 2': 'QUAN 12',
  'Municipal Level 3': 'PHUONG TRUNG MY TAY',
  'Street': 'TO KY',
  'Unparsed': ''}
  ```

#### Spelling error, with modifiable fuzzy match threshold:
##### 1. Default threshold
  ```python
  test_address = "47/9B Tô Ký Q.12 Phường Trung Mĩ Tây TPHCM"
  parser.parse_address(test_address) # default threshold is 95
  ```
  ```python
  {'Country': '',
  'House Number': '47/9B',
  'Municipal Level 1': 'THANH PHO HO CHI MINH',
  'Municipal Level 2': 'QUAN 12',
  'Municipal Level 3': '',
  'Street': 'TO KY',
  'Unparsed': 'PHUONG TRUNG MI TAY'}
  ```

##### 2. Custom threshold
  ```python
  test_address = "47/9B Tô Ký Q.12 Phung Trang Mĩ Tây TPHCM"
  parser.parse_address(test_address, threshold=85)
  ```
  ```python
  {'Country': '',
  'House Number': '47/9B',
  'Municipal Level 1': 'THANH PHO HO CHI MINH',
  'Municipal Level 2': 'QUAN 12',
  'Municipal Level 3': 'PHUONG TRUNG MY TAY',
  'Street': 'TO KY',
  'Unparsed': ''}
  ```

### Required Library:

- `rapidfuzz`

### Limitations:

- Cannot parse old, out-of-use addresses like *Quận 2*, *Quận 9*, etc.
- Parsing addresses with spelling errors will take significantly more time than addresses without.
- Will not parse house numbers for apartment addresses, as it cannot distinguish between the house number of the complex and the unit number.
- In case of invalid addresses like *Quận 3, Hà Nội* (there is no *Quận 3* in *Hà Nội*) the parser will return the most probable parse instead of outright saying the address is invalid

### Data sources:
- Municipal Data: https://github.com/ThangLeQuoc/vietnamese-provinces-database/blob/master/json/simplified_json_generated_data_vn_units.json
The data was subsequently cleaned and transformed by converting to uppercase and removing diacritics as well as leading zeroes for numerical municipal values 