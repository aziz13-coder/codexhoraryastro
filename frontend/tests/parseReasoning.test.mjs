import { parseReasoningEntry } from '../src/utils/parseReasoning.mjs';

function assert(condition, message) {
  if (!condition) {
    throw new Error(message);
  }
}

const res1 = parseReasoningEntry('Good omen (5%)');
assert(res1.rule === 'Good omen' && res1.weight === 5, 'failed to parse parenthetical weight');

const res2 = parseReasoningEntry('Bad sign -3%');
assert(res2.rule === 'Bad sign' && res2.weight === -3, 'failed to parse signed weight');

console.log('parseReasoning tests passed');
