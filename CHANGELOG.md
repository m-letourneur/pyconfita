## 1.0.13 (2022-11-02)

- Added `get_struct` wrapper to load entire struct of key-value based on one schema
- Updated VaultBackend's `get_struct` to limit interactions to one request
- Updated FileBackend to handle error when empty file loaded

## 1.0.12 (2022-10-26)

- Updated logging in Vault backend

## 1.0.11 (2022-10-25)

- Fixed Vault backend caching

## 1.0.10 (2022-10-25)

- Fixed Vault backend caching

## 1.0.9 (2022-10-25)

- Fixed Vault backend caching

## 1.0.8 (2022-10-25)

- Updated requirements to replace `cachetools` by `cacheout` 

## 1.0.7 (2022-10-24)

- Updated requirement cachetools<5.0.0

## 1.0.6 (2022-10-24)

- Update Vault backend: enable key-value store caching

## 1.0.5 (2022-10-21)

- Updated value processing to ease debugging: append all values to list, then process it
- Updated tests

## 1.0.4 (2022-10-21)

- Updated value processing: empty string should not be dumped. Only dump None values.
- Updated README

## 1.0.3 (2022-10-21)

[Missed CHANGELOG update]

## 1.0.2 (2022-10-14)

- Added case sensitivity option in Confita

## 1.0.1 (2022-10-13)

- Updated setup.py and tools

## 1.0.0 (2022-10-13)

- Initialized package
- Added Vault backend
- Added File backend (YAML format)
- Added Dict backend
- Added Environment backend
- Added explicit type conversion support (str, bool, int, float)
