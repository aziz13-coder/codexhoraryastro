import { getUseReasoningV1 } from '../src/utils/useReasoningFlag.mjs';

function assert(condition, message) {
  if (!condition) {
    throw new Error(message);
  }
}

global.window = { location: { search: '' } };
process.env.USE_REASONING_V1 = 'true';
assert(getUseReasoningV1() === true, 'env flag true should enable reasoning v1');

process.env.USE_REASONING_V1 = 'false';
window.location.search = '?useReasoningV1=true';
assert(getUseReasoningV1() === true, 'query param should override env');

window.location.search = '?useReasoningV1=false';
assert(getUseReasoningV1() === false, 'explicit false should disable reasoning v1');

console.log('useReasoningFlag tests passed');
