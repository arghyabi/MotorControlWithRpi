<?php
header('Content-Type: application/json');
require_once 'common.php';

function getStatus() {
    $data = readDb();
    if ($data === false) {
        return ["error" => "rtDb.json not found"];
    }
    return [
        "motorStatus"           => isset($data['motorStatus'])           ? $data['motorStatus']           : 'OFF',
        "tankLevel"             => isset($data['tankLevel'])             ? $data['tankLevel']             : 0,
        "valve1Duration"        => isset($data['valve1Duration'])        ? $data['valve1Duration']        : 1,
        "valve2Duration"        => isset($data['valve2Duration'])        ? $data['valve2Duration']        : 1,
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

function setConfig($key, $value) {
    $data = readDb();
    if ($data === false) {
        return ["error" => "rtDb.json not found"];
    }
    $data[$key] = $value;
    $data['configUpdateAvailable'] = true;
    writeDb($data);
    return ["success" => true, $key => $value];
}

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    if (isset($_POST['motorStatus'])) {
        $motorStatus = $_POST['motorStatus'] === 'ON' ? 'ON' : 'OFF';
        echo json_encode(setMotor($motorStatus));
    } elseif (isset($_POST['valve1Duration'])) {
        echo json_encode(setConfig('valve1Duration', (int)$_POST['valve1Duration']));
    } elseif (isset($_POST['valve2Duration'])) {
        echo json_encode(setConfig('valve2Duration', (int)$_POST['valve2Duration']));
    }
} else {
    echo json_encode(getStatus());
}
