package com.github.telegram_bots.channels_feed.tg.config

import com.github.telegram_bots.channels_feed.tg.util.userInfoParts
import org.springframework.boot.autoconfigure.jdbc.DataSourceProperties
import org.springframework.context.annotation.Bean
import org.springframework.context.annotation.Configuration
import org.springframework.context.annotation.Primary
import org.springframework.core.env.Environment
import org.springframework.jdbc.core.JdbcTemplate
import java.net.URI
import javax.sql.DataSource

@Configuration
class DBConfig {
    @Bean
    fun jdbcTemplate(ds: DataSource) = JdbcTemplate(ds)

    @Bean
    @Primary
    fun dataSourceProperties(env: Environment): DataSourceProperties {
        val uri = env.getProperty("CF_DB_URL").let { URI(it) }
        val (user, pass) = uri.userInfoParts()

        return DataSourceProperties().apply {
            username = user
            password = pass
            url = "jdbc:" + uri.toString().replace("//${uri.userInfo}@", "//")
        }
    }
}
