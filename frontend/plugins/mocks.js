// // mocks.js
// // 1. Import mocking utils
// import { setupWorker, rest } from 'msw'

// // 2. Define request handlers and response resolvers
// const worker = setupWorker(
//   // Mock GET request to list experiments
//   rest.get('/experiments', (req, res, ctx) => {
//     return res(
//       // Specfy delay before response
//       ctx.delay(500),
//       // Send back status code 200 with HTTP label 'Mocked response'
//       ctx.status(200, 'Mocked response'),
//       // Send back JSON response
//       ctx.json({
//         experiments: [1, 2, 3]
//       })
//     )
//   }),
//   // Mock POST request to create Experiment
//   rest.post('/experiments', (req, res, ctx) => {
//     return res(
//       ctx.delay(500),
//       ctx.status(202, 'Mocked response'),
//       ctx.json({
//         id: 1
//       })
//     )
//   })
// )

// // 3. Start the Service Worker
// // TODO: Start the service worker on development mode only
// worker.start()
