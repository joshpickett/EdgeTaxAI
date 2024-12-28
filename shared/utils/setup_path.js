import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

export function setupUtilsPath() {
    const utilsRoot = path.resolve(__dirname, '..');
    
    if (!process.env.NODE_PATH) {
        process.env.NODE_PATH = '';
    }
    
    if (!process.env.NODE_PATH.includes(utilsRoot)) {
        process.env.NODE_PATH = `${utilsRoot}:${process.env.NODE_PATH}`;
    }
    
    require('module').Module._initPaths();
}

export default setupUtilsPath;
