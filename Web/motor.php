<?php
header('Content-Type: application/json');
require_once 'common.php';

function getStatus() {
    $data = readDb();
    if ($data === false) {
        return ["error" => "rtDb.json not found"];
    }
    return [
        "motorStatus" => isset($data['motorStatus']) ? $data['motorStatus'] : 'OFF',
        "tankLevel" => isset($data['tankLevel']) ? $data['tankLevel'] : 0,
        "configUpdateAvailable" => isset($data['configUpdateAvailable']) ? $data['configUpdateAvailable'] : false
    ];
}

function setMotor($motorStatus) {
    $data = readDb();
    if ($data === false) {
        return ["error" => "rtDb.json not found"];
    }
    $data['motorStatus'] = $motorStatus;
    $data['configUpdateAvailable'] = true;
    writeDb($data);
    return ["success" => true, "motorStatus" => $motorStatus];
}

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $motorStatus = isset($_POST['motorStatus']) && $_POST['motorStatus'] === 'ON' ? 'ON' : 'OFF';
    echo json_encode(setMotor($motorStatus));
} else {
    echo json_encode(getStatus());
}
