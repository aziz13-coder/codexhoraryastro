export function getUseReasoningV1() {
  let queryFlag = null;
  if (typeof window !== 'undefined' && window.location) {
    const params = new URLSearchParams(window.location.search);
    queryFlag = params.get('useReasoningV1');
  }
  if (queryFlag !== null) {
    return queryFlag === 'true';
  }
  const envFlag = (import.meta.env && import.meta.env.VITE_USE_REASONING_V1) || process.env.USE_REASONING_V1;
  if (envFlag !== undefined) {
    return String(envFlag).toLowerCase() === 'true';
  }
  return false;
}
