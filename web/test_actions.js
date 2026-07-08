const { getAdminTelemetry } = require('./.next/server/app/admin/actions.js');

async function run() {
  try {
    const res = await getAdminTelemetry();
    console.log("Success:", Object.keys(res));
  } catch (err) {
    console.error("Error:", err);
  }
}

run();
