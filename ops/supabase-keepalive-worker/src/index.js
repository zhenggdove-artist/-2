const DEFAULT_TIMEOUT_MS = 15000;

function jsonResponse(body, status = 200) {
  return new Response(JSON.stringify(body, null, 2), {
    status,
    headers: {
      "content-type": "application/json; charset=utf-8",
      "cache-control": "no-store"
    }
  });
}

function getConfig(env) {
  const supabaseUrl = (env.SUPABASE_URL || "").replace(/\/+$/, "");
  const supabaseKey = env.SUPABASE_PUBLISHABLE_KEY || env.SUPABASE_KEY || "";
  const table = env.SUPABASE_TABLE || "defender_leaderboard";
  const queryCount = Math.max(1, Math.min(10, Number(env.QUERY_COUNT || 1) || 1));

  if (!supabaseUrl) throw new Error("SUPABASE_URL is not configured");
  if (!supabaseKey) throw new Error("SUPABASE_PUBLISHABLE_KEY is not configured");

  return { supabaseUrl, supabaseKey, table, queryCount };
}

async function fetchWithTimeout(url, init, timeoutMs = DEFAULT_TIMEOUT_MS) {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort("timeout"), timeoutMs);

  try {
    return await fetch(url, { ...init, signal: controller.signal });
  } finally {
    clearTimeout(timer);
  }
}

async function pingSupabase(env, reason) {
  const config = getConfig(env);
  const endpoint = `${config.supabaseUrl}/rest/v1/${encodeURIComponent(config.table)}?select=id&limit=1`;
  const startedAt = Date.now();
  const results = [];

  for (let i = 0; i < config.queryCount; i += 1) {
    const response = await fetchWithTimeout(endpoint, {
      headers: {
        "accept": "application/json",
        "apikey": config.supabaseKey,
        "authorization": `Bearer ${config.supabaseKey}`,
        "cache-control": "no-store"
      }
    });

    const body = await response.text();
    results.push({
      attempt: i + 1,
      ok: response.ok,
      status: response.status
    });

    if (!response.ok) {
      throw new Error(`Supabase returned HTTP ${response.status}: ${body.slice(0, 200)}`);
    }
  }

  return {
    ok: true,
    reason,
    table: config.table,
    queryCount: config.queryCount,
    durationMs: Date.now() - startedAt,
    checkedAt: new Date().toISOString(),
    results
  };
}

async function notifyFailure(env, error, controller) {
  if (!env.ALERT_WEBHOOK) return;

  await fetchWithTimeout(env.ALERT_WEBHOOK, {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify({
      text: "Run Artist Run Supabase keepalive failed",
      cron: controller?.cron,
      scheduledTime: controller?.scheduledTime,
      error: error?.message || String(error),
      checkedAt: new Date().toISOString()
    })
  }, 10000);
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);

    if (url.pathname === "/" || url.pathname === "/health") {
      try {
        const result = await pingSupabase(env, "manual-http");
        return jsonResponse(result);
      } catch (error) {
        return jsonResponse({
          ok: false,
          error: error?.message || String(error),
          checkedAt: new Date().toISOString()
        }, 502);
      }
    }

    return jsonResponse({ ok: false, error: "Not found" }, 404);
  },

  async scheduled(controller, env, ctx) {
    try {
      const result = await pingSupabase(env, `cron:${controller.cron}`);
      console.log("[supabase-keepalive] success", JSON.stringify(result));
    } catch (error) {
      console.error("[supabase-keepalive] failure", error?.message || error);
      ctx.waitUntil(notifyFailure(env, error, controller).catch((notifyError) => {
        console.error("[supabase-keepalive] alert failure", notifyError?.message || notifyError);
      }));
      throw error;
    }
  }
};
