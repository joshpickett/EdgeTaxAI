"use strict";

Object.defineProperty(exports, "__esModule", {
  value: true
});
exports.default = _default;

function _chalk() {
  const data = _interopRequireDefault(require("chalk"));

  _chalk = function () {
    return data;
  };

  return data;
}

function _applyAsyncAction() {
  const data = require("./utils/applyAsyncAction");

  _applyAsyncAction = function () {
    return data;
  };

  return data;
}

function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }

function _getRequireWildcardCache(nodeInterop) { if (typeof WeakMap !== "function") return null; var cacheBabelInterop = new WeakMap(); var cacheNodeInterop = new WeakMap(); return (_getRequireWildcardCache = function (nodeInterop) { return nodeInterop ? cacheNodeInterop : cacheBabelInterop; })(nodeInterop); }

function _interopRequireWildcard(obj, nodeInterop) { if (!nodeInterop && obj && obj.__esModule) { return obj; } if (obj === null || typeof obj !== "object" && typeof obj !== "function") { return { default: obj }; } var cache = _getRequireWildcardCache(nodeInterop); if (cache && cache.has(obj)) { return cache.get(obj); } var newObj = {}; var hasPropertyDescriptor = Object.defineProperty && Object.getOwnPropertyDescriptor; for (var key in obj) { if (key !== "default" && Object.prototype.hasOwnProperty.call(obj, key)) { var desc = hasPropertyDescriptor ? Object.getOwnPropertyDescriptor(obj, key) : null; if (desc && (desc.get || desc.set)) { Object.defineProperty(newObj, key, desc); } else { newObj[key] = obj[key]; } } } newObj.default = obj; if (cache) { cache.set(obj, newObj); } return newObj; }

function _default(program) {
  (0, _applyAsyncAction().applyAsyncActionProjectDir)(program.command('upload:android [path]').alias('ua').description('Upload an Android binary to the Google Play Store').helpGroup('upload').option('--latest', 'upload the latest build').option('--id <id>', 'id of the build to upload').option('--path [path]', 'path to the .apk/.aab file').option('--url <url>', 'app archive url').option('--key <key>', 'path to the JSON key used to authenticate with Google Play').option('--android-package <android-package>', 'Android package name (using expo.android.package from app.json by default)').option('--type <archive-type>', 'archive type: apk, aab', /^(apk|aab)$/i).option('--track <track>', 'the track of the application to use, choose from: production, beta, alpha, internal, rollout', /^(production|beta|alpha|internal|rollout)$/i, 'internal').option('--release-status <release-status>', 'release status (used when uploading new apks/aabs), choose from: completed, draft, halted, inProgress', /^(completed|draft|halted|inProgress)$/i, 'completed').option('--use-submission-service', 'Experimental: Use Submission Service for uploading your app. The upload process will happen on Expo servers.').option('--verbose', 'Always print logs from Submission Service'), () => Promise.resolve().then(() => _interopRequireWildcard(require('./upload/uploadAndroidAsync'))));
  (0, _applyAsyncAction().applyAsyncActionProjectDir)(program.command('upload:ios [path]').alias('ui').description(`${_chalk().default.yellow('Unsupported:')} Use ${_chalk().default.bold('eas submit')} or Transporter app instead.`).longDescription('Upload an iOS binary to Apple TestFlight (MacOS only). Uses the latest build by default').helpGroup('upload') // TODO: Remove all props now that this is deprecated
  .option('--latest', 'upload the latest build (default)').option('--id <id>', 'id of the build to upload').option('--path [path]', 'path to the .ipa file').option('--url <url>', 'app archive url').option('--apple-id <apple-id>', 'your Apple ID username (you can also set EXPO_APPLE_ID env variable)') // apple unified App Store Connect and Developer Portal teams, this is temporary solution until fastlane implements those changes
  // https://github.com/fastlane/fastlane/issues/14229
  // after updating fastlane this value will be unnecessary
  .option('--itc-team-id <itc-team-id>', 'App Store Connect Team ID - this option is deprecated, the proper ID is resolved automatically').option('--apple-id-password <apple-id-password>', 'your Apple ID password (you can also set EXPO_APPLE_PASSWORD env variable)').option('--app-name <app-name>', `the name of your app as it will appear on the App Store, this can't be longer than 30 characters (default: expo.name from app.json)`).option('--company-name <company-name>', 'the name of your company, needed only for the first upload of any app to App Store').option('--sku <sku>', 'a unique ID for your app that is not visible on the App Store, will be generated unless provided').option('--language <language>', `primary language (e.g. English, German; run \`expo upload:ios --help\` to see the list of available languages)`, 'English').option('--public-url <url>', 'The URL of an externally hosted manifest (for self-hosted apps)'), () => Promise.resolve().then(() => _interopRequireWildcard(require('./upload/uploadIosAsync'))));
}
//# sourceMappingURL=upload.js.map