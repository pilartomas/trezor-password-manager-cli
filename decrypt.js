fs = require("fs");
crypto = require("crypto");

const CIPHER_IVSIZE = 96 / 8;
const AUTH_SIZE = 128 / 8;
const CIPHER_TYPE = "aes-256-gcm";

function decrypt(key, data) {
  try {
    let iv = data.slice(0, CIPHER_IVSIZE),
      auth_tag = data.slice(CIPHER_IVSIZE, CIPHER_IVSIZE + AUTH_SIZE),
      cText = data.slice(CIPHER_IVSIZE + AUTH_SIZE),
      decipher = crypto.createDecipheriv(CIPHER_TYPE, key, iv),
      start = decipher.update(cText);
    decipher.setAuthTag(auth_tag);
    let end = decipher.final();
    return Buffer.concat([start, end]).toString("utf8");
  } catch (error) {
    console.error("error ", error);
    return new Buffer([]).toString("utf8");
    //TODO
  }
}

const key = Buffer.from(process.argv[2], "hex");
const data = fs.readFileSync("/dev/stdin");
const result = decrypt(key, data);
process.stdout.write(result);
