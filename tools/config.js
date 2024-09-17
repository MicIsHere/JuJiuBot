const database = 'JuJiuBot';
const collection = 'config';

use(database);

db.getCollection(config)
    .updateOne(
        {
            "account": 2415838976
        }, 
        {
            "$set": {
                "security": true,
                "auto_accept": true,
                "admins": [
                    3098880154
                ]
            }
        }, 
        {
            "upsert": true
        }
    );