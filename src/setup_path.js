import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

export function setupSrcPath() {
    const srcRoot = path.resolve(__dirname);
    const sharedRoot = path.resolve(__dirname, '../shared');
    
    if (!process.env.NODE_PATH) {
        process.env.NODE_PATH = '';
    }
    
    // Add both src and shared roots to NODE_PATH
    const paths = [srcRoot, sharedRoot].filter(p => !process.env.NODE_PATH.includes(p));
    if (paths.length) {
        process.env.NODE_PATH = `${paths.join(':')}:${process.env.NODE_PATH}`;
    }
    
    require('module').Module._initPaths();
}

export default setupSrcPath;
