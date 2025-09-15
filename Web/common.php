<?php
function getDbPath() {
    return realpath(__DIR__ . '/../rtDb.json');
}

function readDb() {
    $dbPath = getDbPath();
    if (!file_exists($dbPath)) {
        return false;
    }
    $json = file_get_contents($dbPath);
    $data = json_decode($json, true);
    if ($data === null && json_last_error() !== JSON_ERROR_NONE) {
        error_log('Invalid JSON in rtDb.json: ' . json_last_error_msg());
        // Optionally, you can return an empty array or false
        return [];
    }
    return $data;
}

function writeDb($data) {
    $dbPath = getDbPath();
    $result = file_put_contents($dbPath, json_encode($data));
    if ($result === false) {
        error_log('Failed to write to rtDb.json');
        return false;
    }
    return true;
}
