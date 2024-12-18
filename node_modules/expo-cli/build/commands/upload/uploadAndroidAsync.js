"use strict";

Object.defineProperty(exports, "__esModule", {
  value: true
});
exports.actionAsync = actionAsync;

function _log() {
  const data = _interopRequireDefault(require("../../log"));

  _log = function () {
    return data;
  };

  return data;
}

function _AndroidSubmitCommand() {
  const data = _interopRequireDefault(require("../upload/submission-service/android/AndroidSubmitCommand"));

  _AndroidSubmitCommand = function () {
    return data;
  };

  return data;
}

function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }

async function actionAsync(projectRoot, options) {
  if (options.useSubmissionService) {
    _log().default.warn('\n`--use-submission-service is now the default and the flag will be deprecated in the future.`');
  }

  const ctx = _AndroidSubmitCommand().default.createContext(projectRoot, options);

  const command = new (_AndroidSubmitCommand().default)(ctx);
  await command.runAsync();
}
//# sourceMappingURL=uploadAndroidAsync.js.map