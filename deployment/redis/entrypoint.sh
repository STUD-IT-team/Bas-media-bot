mkdir -p /usr/local/etc/redis
echo "requirepass $REDIS_PASSWORD" > /usr/local/etc/redis/redis.conf
echo "user $REDIS_USER on >$REDIS_USER_PASSWORD ~* +@all" > /usr/local/etc/redis/users.acl
# echo "aclfile /usr/local/etc/redis/users.acl >> /usr/local/etc/redis/redis.conf"
redis-server /usr/local/etc/redis/redis.conf --aclfile /usr/local/etc/redis/users.acl
