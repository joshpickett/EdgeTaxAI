No content yet
            // Add platform-specific headers
            if (config.platform) {
                config.headers['X-Platform'] = config.platform;
                config.headers['X-Platform-Version'] = config.platformVersion || '1.0';
            }

            if (token) {
                config.headers.Authorization = `Bearer ${token}`;
            }

                            // Update platform-specific tokens if needed
                            if (response.data.platformTokens) {
                                Object.entries(response.data.platformTokens).forEach(([platform, token]) => {
                                    localStorage.setItem(`${platform}_token`, token);
                                });
                            }
                            error.config.headers.Authorization = `Bearer ${response.data.token}`;
                            return this.client(error.config);
                        } catch (refreshError) {
