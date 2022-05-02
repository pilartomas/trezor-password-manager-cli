# Trezor Password Manager CLI

Command-line alternative to the [Trezor Password Manager](https://trezor.io/passwords/) project. This project is aiming for compatibility in password store encryption, encoding and structure. Users will be able to read and write to the same password store regardless of which project they use.

### Run

- Install with pip: `$ pip install trezor-pass`
- Run: `$ trezor-pass`

### Limitations

Current version has some limitations

- Only reading is supported at the moment, store creation and updates will come later on.
- Tested on Trezor One. Some additional complexity around PASSPHRASE on Trezor T needs to be handled. (Might be bypassed by correctly setting the PASSPHRASE env variable)
- Google Drive storage is not yet supported (Can be bypassed by direcly specifying the store file)
