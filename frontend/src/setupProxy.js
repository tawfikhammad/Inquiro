const { createProxyMiddleware } = require('http-proxy-middleware');

const isDocker = process.env.DOCKER_ENV === 'true';
const backendUrl = isDocker ? 'http://backend-dev:5000' : 'http://localhost:5000';

module.exports = function (app) {
    app.use(
        ['/projects', '/papers', '/summaries', '/rag', '/translator', '/explainer'],
        createProxyMiddleware({
            target: backendUrl,
            changeOrigin: true,
            onError: (err, req, res) => {
                console.error('Proxy error:', err.message);
                res.status(500).json({
                    error: 'Backend connection failed',
                    details: err.message,
                    target: backendUrl
                });
            },
            onProxyReq: (proxyReq, req, res) => {
                console.log(`Proxying ${req.method} ${req.path} to ${backendUrl}`);
            }
        })
    );
};