const express = require("express");
const jwt = require("jsonwebtoken");
const cors = require("cors");

const app = express();
app.use(cors()); // Mengizinkan HP / perangkat lain mengakses API ini

const METABASE_SECRET_KEY = "4cd02488cc4371d354339da008330b054fa9a9d5db6b3bcbe372ed5712d3ae01";

app.get("/api/metabase-token", (req, res) => {
  const payload = {
    resource: { dashboard: 34 },
    params: {},
    exp: Math.round(Date.now() / 1000) + (10 * 60) 
  };

  const token = jwt.sign(payload, METABASE_SECRET_KEY);
  res.json({ token: token });
});

const PORT = 5000;
// Mengatur agar server mendengarkan request dari semua perangkat di jaringan lokal
app.listen(PORT, "0.0.0.0", () => {
  console.log(`Server backend berjalan di jaringan lokal.`);
});