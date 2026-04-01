// Dummy test script for relay testing
const args = process.argv.slice(2);
if (args.includes('--fail') || args.includes('true') && args.some(a => a === '--fail')) {
  console.error('Intentional failure for testing');
  process.exit(1);
} else if (args.includes('--invalid_json')) {
  console.log('this is not json output at all');
} else {
  console.log(JSON.stringify({status: "ok", result: "approved"}));
}
