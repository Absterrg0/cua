#!/usr/bin/env node
/**
 * Sign one extension catalog payload with an Ed25519 key.
 *
 * Usage: sign_extension_catalog.mjs <catalog-payload.json> <private-key.pem> <trust-root.json> <out-dir>
 *
 * The signature covers the exact payload bytes that `perception_release.py
 * package` wrote, which equal the Driver's own compact serialization of the
 * payload. The key must be the trust root's active key, and the signature is
 * verified with that published public key before anything is written.
 */
import crypto from "node:crypto"
import fs from "node:fs"
import path from "node:path"

const [payloadPath, keyPath, trustPath, outDir] = process.argv.slice(2)
if (!payloadPath || !keyPath || !trustPath || !outDir) {
  throw new Error("usage: sign_extension_catalog.mjs <payload> <private-key.pem> <trust-root.json> <out-dir>")
}
const payloadBytes = fs.readFileSync(payloadPath)
const payload = JSON.parse(payloadBytes)
const trust = JSON.parse(fs.readFileSync(trustPath, "utf8"))
const active = trust.keys.filter((key) => key.keyId === trust.activeKeyId && key.status === "active")
if (active.length !== 1) throw new Error("trust root has no unique active key")
if (payload.key_id !== trust.activeKeyId || payload.publisher_id !== trust.publisherId) {
  throw new Error("catalog payload names a different publisher or key than the trust root")
}
const privateKey = crypto.createPrivateKey(fs.readFileSync(keyPath))
const publicKey = crypto.createPublicKey({
  key: Buffer.concat([
    Buffer.from("302a300506032b6570032100", "hex"),
    Buffer.from(active[0].publicKeyBase64, "base64"),
  ]),
  format: "der",
  type: "spki",
})
const signature = crypto.sign(null, payloadBytes, privateKey)
if (signature.length !== 64 || !crypto.verify(null, payloadBytes, publicKey, signature)) {
  throw new Error("the private key does not match the trust root's active public key")
}
fs.mkdirSync(outDir, { recursive: true })
fs.writeFileSync(path.join(outDir, "catalog.signature"), signature)
fs.writeFileSync(
  path.join(outDir, "signed-catalog.json"),
  `${JSON.stringify({ payload, signature_algorithm: "ed25519", signature: signature.toString("base64") })}\n`,
)
console.log(path.join(outDir, "signed-catalog.json"))
