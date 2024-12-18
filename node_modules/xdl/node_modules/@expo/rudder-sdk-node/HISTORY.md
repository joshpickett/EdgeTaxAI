v1.1.0
==========================

### Breaking changes

* The main Analytics class is now a default export instead of being the value of `module.exports`. If you're using `require` with this library, you'll need to write `require('@expo/rudder-sdk-node').default`. If you're using `import` with this library, no changes are needed
* Removed support for persisting events in Redis
* Changed the logger from `winston` to `bunyan` (specifically, `@expo/bunyan`)
* Changed the default log level from INFO to FATAL
* The `timeout` option must be a number (milliseconds). Strings are no longer supported. As before, 0 means no timeout but now negative numbers also disable timeouts
* Changed how `flush()` works
    * `flush()` now sends all messages present in the message queue at the time of the request
        * previously `flush()` would only send `flushAt` number of events
    * `flush()` now guards against batch sizes too large for the server via the configurable `maxFlushSizeInBytes` property. Trimmed messages remain in the queue for subsequent HTTP requests
    * `flush()` now enforces a limit of one concurrent HTTP request at a time
        * simultaneous `flush()` requests will be handled when the current HTTP request finishes
    * Flushing will now occur
        * the first time an event is enqueued after instantiation (occurs immediately)
        * when the message queue size is divisible by `flushAt` (occurs immediately)
        * when a new event is enqueued after a flush (a timer is set for flush to occur after `flushInterval` ms)
        * when a user requests a `flush()`
    * `flush()` is now an async function
    * `flush()` now has a return type of `Promise<FlushResponse[]>`
    * flush callbacks now accept arguments of type `FlushResponse[]`
    * `flush()` no longer throws upon failure but returns an error object instead
    * Changed when fetch requests are retried - All network errors are retried
* No longer causes an exiting process to indefinitely stall due to a looping timer. If a process is naturally exiting (not due to `process.exit()`), you must call `analytics.flush()` to send the last events for them to be sent
* The `userId` and `anonymousId` message fields must be primitive strings. Other types like numbers are not supported

### Minor changes

* Convert from JavaScript to TypeScript. First-class type 
* Replaced `axios` with `node-fetch`
* The library name in the log context object is now `@expo/rudder-sdk-node`
* The user agent string is now `expo-rudder-sdk-node/<version>`
* enqueue now limits the max events in the queue via configurable `maxQueueLength` property.  If `enqueue()` is called and the message queue is already at or above the `maxQueueLength` that message is dropped

v1.0.8
==========================

Based on 1.0.3+ of [`@rudderstack/rudder-sdk-node`](https://github.com/rudderlabs/rudder-sdk-node/commit/8060ec7303df24491664686f6cf2620a2436797f).

* Consistently use winston instead of console.log for logging
