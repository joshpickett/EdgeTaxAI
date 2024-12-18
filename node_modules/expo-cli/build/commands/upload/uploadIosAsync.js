"use strict";

Object.defineProperty(exports, "__esModule", {
  value: true
});
exports.actionAsync = actionAsync;

function _chalk() {
  const data = _interopRequireDefault(require("chalk"));

  _chalk = function () {
    return data;
  };

  return data;
}

function _log() {
  const data = _interopRequireDefault(require("../../log"));

  _log = function () {
    return data;
  };

  return data;
}

function TerminalLink() {
  const data = _interopRequireWildcard(require("../utils/TerminalLink"));

  TerminalLink = function () {
    return data;
  };

  return data;
}

function _getRequireWildcardCache(nodeInterop) { if (typeof WeakMap !== "function") return null; var cacheBabelInterop = new WeakMap(); var cacheNodeInterop = new WeakMap(); return (_getRequireWildcardCache = function (nodeInterop) { return nodeInterop ? cacheNodeInterop : cacheBabelInterop; })(nodeInterop); }

function _interopRequireWildcard(obj, nodeInterop) { if (!nodeInterop && obj && obj.__esModule) { return obj; } if (obj === null || typeof obj !== "object" && typeof obj !== "function") { return { default: obj }; } var cache = _getRequireWildcardCache(nodeInterop); if (cache && cache.has(obj)) { return cache.get(obj); } var newObj = {}; var hasPropertyDescriptor = Object.defineProperty && Object.getOwnPropertyDescriptor; for (var key in obj) { if (key !== "default" && Object.prototype.hasOwnProperty.call(obj, key)) { var desc = hasPropertyDescriptor ? Object.getOwnPropertyDescriptor(obj, key) : null; if (desc && (desc.get || desc.set)) { Object.defineProperty(newObj, key, desc); } else { newObj[key] = obj[key]; } } } newObj.default = obj; if (cache) { cache.set(obj, newObj); } return newObj; }

function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }

async function actionAsync() {
  const logItem = (name, link) => {
    _log().default.log(`\u203A ${TerminalLink().linkedText(name, link)}`);
  };

  _log().default.newLine();

  _log().default.log(_chalk().default.yellow('expo upload:ios is no longer supported'));

  _log().default.log('Please use one of the following');

  _log().default.newLine();

  logItem(_chalk().default.cyan.bold('eas submit'), 'https://docs.expo.dev/submit/ios');
  logItem('Transporter', 'https://apps.apple.com/us/app/transporter/id1450874784');
  logItem('Fastlane deliver', 'https://docs.fastlane.tools/getting-started/ios/appstore-deployment');

  _log().default.newLine();
}
//# sourceMappingURL=uploadIosAsync.js.map