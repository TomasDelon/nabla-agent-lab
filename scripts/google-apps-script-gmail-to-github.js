// Google Apps Script bridge: Gmail -> GitHub repository_dispatch
//
// Install manually in script.google.com.
// Required script properties:
// - GITHUB_TOKEN: fine-grained token allowed to dispatch repository events for TomasDelon/nabla-agent-lab
// - GITHUB_REPO: TomasDelon/nabla-agent-lab
//
// Add a time trigger every 5 minutes or every 10 minutes.

const DEFAULT_REPO = 'TomasDelon/nabla-agent-lab';
const DISPATCH_EVENT_TYPE = 'nabla_email_prompt';
const PROCESSED_LABEL = 'NABLA_DISPATCHED';
const FAILED_LABEL = 'NABLA_DISPATCH_FAILED';

function pollNablaPromptEmails() {
  const props = PropertiesService.getScriptProperties();
  const token = props.getProperty('GITHUB_TOKEN');
  const repo = props.getProperty('GITHUB_REPO') || DEFAULT_REPO;

  if (!token) {
    throw new Error('Missing script property GITHUB_TOKEN');
  }

  const processedLabel = getOrCreateLabel_(PROCESSED_LABEL);
  const failedLabel = getOrCreateLabel_(FAILED_LABEL);
  const query = 'subject:"[NABLA][PROMPT]" newer_than:7d -label:' + PROCESSED_LABEL + ' -label:' + FAILED_LABEL;
  const threads = GmailApp.search(query, 0, 10);

  for (const thread of threads) {
    try {
      const messages = thread.getMessages();
      const message = messages[messages.length - 1];
      const subject = message.getSubject();
      const body = message.getPlainBody();

      const payload = parsePromptEmail_(subject, body, repo);
      validatePayload_(payload, repo);
      dispatchToGitHub_(repo, token, payload);
      thread.addLabel(processedLabel);
    } catch (error) {
      thread.addLabel(failedLabel);
      sendFailureEmail_(thread, error);
    }
  }
}

function parsePromptEmail_(subject, body, fallbackRepo) {
  const runMatch = subject.match(/\[RUN:([^\]]+)\]/);
  const builderMatch = subject.match(/\[BUILDER-([^\]]+)\]/);

  if (!runMatch || !builderMatch) {
    throw new Error('Subject must include [BUILDER-*] and [RUN:*] tags');
  }

  const parsed = JSON.parse(extractJson_(body));
  const runId = runMatch[1].trim();
  const builder = 'builder-' + builderMatch[1].toLowerCase().trim();

  return {
    kind: parsed.kind || 'prompt',
    repo: parsed.repo || fallbackRepo,
    run_id: parsed.run_id || runId,
    builder: parsed.builder || builder,
    base_branch: parsed.base_branch || 'main',
    branch: parsed.branch || ('agent/' + runId),
    report_path: parsed.report_path || ('.nabla-agent/runs/' + runId),
    allowed_paths: parsed.allowed_paths || ['src/**', 'tests/**'],
    forbidden_paths: parsed.forbidden_paths || ['.github/**', 'package.json'],
    task: parsed.task,
    acceptance: parsed.acceptance || ['npm test passes', 'diff touches only allowed paths', 'report files are generated'],
    source_email_subject: subject,
  };
}

function extractJson_(body) {
  const trimmed = body.trim();

  if (trimmed.startsWith('{')) {
    return trimmed;
  }

  const fenced = trimmed.match(/```json\s*([\s\S]*?)\s*```/i);
  if (fenced) {
    return fenced[1].trim();
  }

  const first = trimmed.indexOf('{');
  const last = trimmed.lastIndexOf('}');
  if (first >= 0 && last > first) {
    return trimmed.slice(first, last + 1);
  }

  throw new Error('Email body does not contain a JSON object');
}

function validatePayload_(payload, expectedRepo) {
  const errors = [];

  if (payload.kind !== 'prompt') errors.push('kind must be prompt');
  if (payload.repo !== expectedRepo) errors.push('repo must be ' + expectedRepo);
  if (!payload.run_id) errors.push('run_id is required');
  if (!payload.builder) errors.push('builder is required');
  if (!payload.task) errors.push('task is required');
  if (!Array.isArray(payload.allowed_paths)) errors.push('allowed_paths must be an array');
  if (!Array.isArray(payload.forbidden_paths)) errors.push('forbidden_paths must be an array');
  if (!Array.isArray(payload.acceptance)) errors.push('acceptance must be an array');

  if (errors.length) {
    throw new Error('Invalid JSON prompt payload: ' + errors.join('; '));
  }
}

function dispatchToGitHub_(repo, token, payload) {
  const url = 'https://api.github.com/repos/' + repo + '/dispatches';
  const response = UrlFetchApp.fetch(url, {
    method: 'post',
    contentType: 'application/json',
    headers: {
      Authorization: 'Bearer ' + token,
      Accept: 'application/vnd.github+json',
      'X-GitHub-Api-Version': '2022-11-28',
    },
    payload: JSON.stringify({
      event_type: DISPATCH_EVENT_TYPE,
      client_payload: payload,
    }),
    muteHttpExceptions: true,
  });

  const code = response.getResponseCode();
  if (code < 200 || code >= 300) {
    throw new Error('GitHub dispatch failed: ' + code + ' ' + response.getContentText());
  }
}

function sendFailureEmail_(thread, error) {
  const subject = '[NABLA][DISPATCH][FAILED] ' + thread.getFirstMessageSubject();
  const body = JSON.stringify({
    kind: 'dispatch_failure',
    error: String(error && error.message ? error.message : error),
    source_subject: thread.getFirstMessageSubject(),
  }, null, 2);

  GmailApp.sendEmail('tomas.delon.gago@gmail.com', subject, body);
}

function getOrCreateLabel_(name) {
  return GmailApp.getUserLabelByName(name) || GmailApp.createLabel(name);
}
