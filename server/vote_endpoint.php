<?php
// Pool Room ballot endpoint — drop on any PHP host (e.g. codeonline.io).
// Receives the ballot JSON the vote.html form POSTs and appends it as one
// JSON line to ballots.jsonl (server-side, not web-readable if you place
// the file outside the web root or protect it). Returns 200 + CORS.
//
// Point the ballot at it by setting ENDPOINT in analysis/build_vote.py to
// this file's public URL, then rebuild vote.html.

header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: POST, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type');
if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') { http_response_code(204); exit; }
if ($_SERVER['REQUEST_METHOD'] !== 'POST') { http_response_code(405); exit; }

$raw = file_get_contents('php://input');
$b = json_decode($raw, true);
if (!is_array($b) || !isset($b['fourTwo']) || !isset($b['threeThree'])) {
    http_response_code(400);
    echo json_encode(['ok' => false, 'error' => 'malformed ballot']);
    exit;
}
// stamp server-side receipt info (client ts/name are self-reported)
$rec = [
    'name'        => substr((string)($b['name'] ?? ''), 0, 80),
    'stakeholder' => (string)($b['stakeholder'] ?? ''),
    'fourTwo'     => array_slice((array)$b['fourTwo'], 0, 2),
    'threeThree'  => array_slice((array)$b['threeThree'], 0, 2),
    'comment'     => substr((string)($b['comment'] ?? ''), 0, 500),
    'client_ts'   => (string)($b['ts'] ?? ''),
    'server_ts'   => gmdate('c'),
    'ip'          => $_SERVER['REMOTE_ADDR'] ?? '',
];
$fp = fopen(__DIR__ . '/ballots.jsonl', 'a');
if ($fp) { flock($fp, LOCK_EX);
    fwrite($fp, json_encode($rec, JSON_UNESCAPED_UNICODE) . "\n");
    flock($fp, LOCK_UN); fclose($fp); }
http_response_code(200);
echo json_encode(['ok' => true]);
